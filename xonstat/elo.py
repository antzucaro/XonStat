import datetime
import logging
import math

from xonstat.models import PlayerElo

log = logging.getLogger(__name__)


class EloParms:
    def __init__(self, global_K=15, initial=100, floor=100,
                 logdistancefactor=math.log(10)/float(400), maxlogdistance=math.log(10),
                 latencyfactor=0.2):
        self.global_K = global_K
        self.initial = initial
        self.floor = floor
        self.logdistancefactor = logdistancefactor
        self.maxlogdistance = maxlogdistance
        self.latencyfactor = latencyfactor


class KReduction:
    def __init__(self, fulltime, mintime, minratio, games_min, games_max, games_factor):
        self.fulltime = fulltime
        self.mintime = mintime
        self.minratio = minratio
        self.games_min = games_min
        self.games_max = games_max
        self.games_factor = games_factor

    def eval(self, mygames, mytime, matchtime):
        if mytime < self.mintime:
            return 0
        if mytime < self.minratio * matchtime:
            return 0
        if mytime < self.fulltime:
            k = mytime / float(self.fulltime)
        else:
            k = 1.0
        if mygames >= self.games_max:
            k *= self.games_factor
        elif mygames > self.games_min:
            k *= 1.0 - (1.0 - self.games_factor) * (mygames - self.games_min) / float(self.games_max - self.games_min)
        return k


# parameters for K reduction
# this may be touched even if the DB already exists
KREDUCTION = KReduction(600, 120, 0.5, 0, 32, 0.2)

# parameters for chess elo
# only global_K may be touched even if the DB already exists
# we start at K=200, and fall to K=40 over the first 20 games
ELOPARMS = EloParms(global_K = 200)


class EloWIP:
    """EloWIP is a work-in-progress Elo value. It contains all of the
    attributes necessary to calculate Elo deltas for a given game."""
    def __init__(self, player_id, pgstat=None):
        # player_id this belongs to
        self.player_id = player_id

        # score per second in the game
        self.score_per_second = 0.0

        # seconds alive during a given game
        self.alivetime = 0

        # current elo record
        self.elo = None

        # current player_game_stat record
        self.pgstat = pgstat

        # Elo algorithm K-factor 
        self.k = 0.0

        # Elo points accumulator, which is not adjusted by the K-factor
        self.adjustment = 0.0

        # elo points delta accumulator for the game, which IS adjusted 
        # by the K-factor
        self.elo_delta = 0.0

    def should_save(self):
        """Determines if the elo and pgstat attributes of this instance should
        be persisted to the database"""
        return self.k > 0.0

    def __repr__(self):
        return "<EloWIP(player_id={}, score_per_second={}, alivetime={}, \
                elo={}, pgstat={}, k={}, adjustment={}, elo_delta={})>".\
                format(self.player_id, self.score_per_second, self.alivetime, \
                self.elo, self.pgstat, self.k, self.adjustment, self.elo_delta)


class EloProcessor:
    """EloProcessor is a container for holding all of the intermediary AND
    final values used to calculate Elo deltas for all players in a given
    game."""
    def __init__(self, session, game, pgstats):

        # game which we are processing
        self.game = game

        # work-in-progress values, indexed by player
        self.wip = {}

        # used to determine if a pgstat record is elo-eligible
        def elo_eligible(pgs):
            return pgs.player_id > 2 and pgs.alivetime > datetime.timedelta(seconds=0)

        elostats = filter(elo_eligible, pgstats)

        # only process elos for elo-eligible players
        for pgstat in elostats:
            self.wip[pgstat.player_id] = EloWIP(pgstat.player_id, pgstat)

        # determine duration from the maximum alivetime
        # of the players if the game doesn't have one
        self.duration = 0
        if game.duration is not None:
            self.duration = game.duration.seconds
        else:
            self.duration = max(i.alivetime.seconds for i in elostats)

        # Calculate the score_per_second and alivetime values for each player.
        # Warmups may mess up the player alivetime values, so this is a 
        # failsafe to put the alivetime ceiling to be the game's duration.
        for e in self.wip.values():
            if e.pgstat.alivetime.seconds > self.duration:
                e.score_per_second = e.pgstat.score/float(self.duration)
                e.alivetime = self.duration
            else:
                e.score_per_second = e.pgstat.score/float(e.pgstat.alivetime.seconds)
                e.alivetime = e.pgstat.alivetime.seconds

        # Fetch current Elo values for all players. For players that don't yet 
        # have an Elo record, we'll give them a default one.
        for e in session.query(PlayerElo).\
                filter(PlayerElo.player_id.in_(self.wip.keys())).\
                filter(PlayerElo.game_type_cd==game.game_type_cd).all():
                    self.wip[e.player_id].elo = e

        for pid in self.wip.keys():
            if self.wip[pid].elo is None:
                self.wip[pid].elo = PlayerElo(pid, game.game_type_cd, ELOPARMS.initial)

            # determine k reduction
            self.wip[pid].k = KREDUCTION.eval(self.wip[pid].elo.games, self.wip[pid].alivetime,
                                              self.duration)

        # we don't process the players who have a zero K factor
        self.wip = {e.player_id:e for e in self.wip.values() if e.k > 0.0}

        # now actually process elos
        self.process()

    def scorefactor(self, si, sj):
        """Calculate the real scorefactor of the game. This is how players
        actually performed, which is compared to their expected performance as
        predicted by their Elo values."""
        scorefactor_real = si / float(si + sj)

        # duels are done traditionally - a win nets
        # full points, not the score factor
        if self.game.game_type_cd == 'duel':
            # player i won
            if scorefactor_real > 0.5:
                scorefactor_real = 1.0
            # player j won
            elif scorefactor_real < 0.5:
                scorefactor_real = 0.0
            # nothing to do here for draws

        return scorefactor_real

    def pingfactor(self, pi, pj):
        """ Calculate the ping differences between the two players, but only if both have them. """
        if pi is None or pj is None or pi < 0 or pj < 0:
            return None

        else:
            return float(pi)/(pi+pj)

    def process(self):
        """Perform the core Elo calculation, storing the values in the "wip"
        dict for passing upstream."""
        if len(self.wip.keys()) < 2:
            return

        ep = ELOPARMS

        pids = self.wip.keys()
        for i in xrange(0, len(pids)):
            ei = self.wip[pids[i]].elo
            for j in xrange(i+1, len(pids)):
                ej = self.wip[pids[j]].elo
                si = self.wip[pids[i]].score_per_second
                sj = self.wip[pids[j]].score_per_second

                # normalize scores
                ofs = min(0, si, sj)
                si -= ofs
                sj -= ofs
                if si + sj == 0:
                    si, sj = 1, 1 # a draw

                # real score factor
                scorefactor_real = self.scorefactor(si, sj)

                # expected score factor by elo
                elodiff = min(ep.maxlogdistance, max(-ep.maxlogdistance,
                    (float(ei.elo) - float(ej.elo)) * ep.logdistancefactor))
                scorefactor_elo = 1 / (1 + math.exp(-elodiff))

                # initial adjustment values, which we may modify with additional rules
                adjustmenti = scorefactor_real - scorefactor_elo
                adjustmentj = scorefactor_elo - scorefactor_real

                # DEBUG
                # log.debug("(New) Player i: {0}".format(ei.player_id))
                # log.debug("(New) Player i's K: {0}".format(self.wip[pids[i]].k))
                # log.debug("(New) Player j: {0}".format(ej.player_id))
                # log.debug("(New) Player j's K: {0}".format(self.wip[pids[j]].k))
                # log.debug("(New) Scorefactor real: {0}".format(scorefactor_real))
                # log.debug("(New) Scorefactor elo: {0}".format(scorefactor_elo))
                # log.debug("(New) adjustment i: {0}".format(adjustmenti))
                # log.debug("(New) adjustment j: {0}".format(adjustmentj))

                if scorefactor_elo > 0.5:
                    # player i is expected to win
                    if scorefactor_real > 0.5:
                        # he DID win, so he should never lose points.
                        adjustmenti = max(0, adjustmenti)
                    else:
                        # he lost, but let's make it continuous
                        # (making him lose less points in the result)
                        adjustmenti = (2 * scorefactor_real - 1) * scorefactor_elo
                else:
                    # player j is expected to win
                    if scorefactor_real > 0.5:
                        # he lost, but let's make it continuous
                        # (making him lose less points in the result)
                        adjustmentj = (1 - 2 * scorefactor_real) * (1 - scorefactor_elo)
                    else:
                        # he DID win, so he should never lose points.
                        adjustmentj = max(0, adjustmentj)

                self.wip[pids[i]].adjustment += adjustmenti
                self.wip[pids[j]].adjustment += adjustmentj

        for pid in pids:
            w = self.wip[pid]
            old_elo = float(w.elo.elo)
            new_elo = max(float(w.elo.elo) + w.adjustment * w.k * ep.global_K / float(len(pids) - 1), ep.floor)
            w.elo_delta = new_elo - old_elo

            w.elo.elo = new_elo
            w.elo.games += 1
            w.elo.update_dt = datetime.datetime.utcnow()

    def save(self, session):
        """Put all changed PlayerElo and PlayerGameStat instances into the
        session to be updated or inserted upon commit."""
        # first, save all of the player_elo values
        for w in self.wip.values():
            session.add(w.elo)

            try:
                w.pgstat.elo_delta = w.elo_delta
                session.add(w.pgstat)
            except:
                log.debug("Unable to save Elo delta value for player_id {0}".format(w.player_id))

