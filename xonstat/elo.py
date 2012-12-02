import datetime
import logging
import math
import random
import sys
from xonstat.models import *


log = logging.getLogger(__name__)


class EloParms:
    def __init__(self, global_K = 15, initial = 100, floor = 100, logdistancefactor = math.log(10)/float(400), maxlogdistance = math.log(10)):
        self.global_K = global_K
        self.initial = initial
        self.floor = floor
        self.logdistancefactor = logdistancefactor
        self.maxlogdistance = maxlogdistance


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


def process_elos(game, session, game_type_cd=None):
    if game_type_cd is None:
        game_type_cd = game.game_type_cd

    # we do not have the actual duration of the game, so use the 
    # maximum alivetime of the players instead
    duration = 0
    for d in session.query(sfunc.max(PlayerGameStat.alivetime)).\
                filter(PlayerGameStat.game_id==game.game_id).\
                one():
        duration = d.seconds

    scores = {}
    alivetimes = {}
    for (p,s,a) in session.query(PlayerGameStat.player_id, 
            PlayerGameStat.score, PlayerGameStat.alivetime).\
            filter(PlayerGameStat.game_id==game.game_id).\
            filter(PlayerGameStat.alivetime > timedelta(seconds=0)).\
            filter(PlayerGameStat.player_id > 2).\
            all():
                # scores are per second
                # with a short circuit to handle alivetimes > game
                # durations, which can happen due to warmup being
                # included (most often in duels)
                if game.duration is not None and a.seconds > game.duration.seconds:
                    scores[p] = s/float(game.duration.seconds)
                    alivetimes[p] = game.duration.seconds
                else:
                    scores[p] = s/float(a.seconds)
                    alivetimes[p] = a.seconds

    player_ids = scores.keys()

    elos = {}
    for e in session.query(PlayerElo).\
            filter(PlayerElo.player_id.in_(player_ids)).\
            filter(PlayerElo.game_type_cd==game_type_cd).all():
                elos[e.player_id] = e

    # ensure that all player_ids have an elo record
    for pid in player_ids:
        if pid not in elos.keys():
            elos[pid] = PlayerElo(pid, game_type_cd, ELOPARMS.initial)

    for pid in player_ids:
        elos[pid].k = KREDUCTION.eval(elos[pid].games, alivetimes[pid],
                duration)
        if elos[pid].k == 0:
            del(elos[pid])
            del(scores[pid])
            del(alivetimes[pid])

    elos = update_elos(game, session, elos, scores, ELOPARMS)

    # add the elos to the session for committing
    for e in elos:
        session.add(elos[e])


def update_elos(game, session, elos, scores, ep):
    if len(elos) < 2:
        return elos

    pids = elos.keys()

    eloadjust = {}
    for pid in pids:
        eloadjust[pid] = 0.0

    for i in xrange(0, len(pids)):
        ei = elos[pids[i]]
        for j in xrange(i+1, len(pids)):
            ej = elos[pids[j]]
            si = scores[ei.player_id]
            sj = scores[ej.player_id]

            # normalize scores
            ofs = min(0, si, sj)
            si -= ofs
            sj -= ofs
            if si + sj == 0:
                si, sj = 1, 1 # a draw

            # real score factor
            scorefactor_real = si / float(si + sj)

            # duels are done traditionally - a win nets
            # full points, not the score factor
            if game.game_type_cd == 'duel':
                # player i won
                if scorefactor_real > 0.5:
                    scorefactor_real = 1.0
                # player j won
                elif scorefactor_real < 0.5:
                    scorefactor_real = 0.0
                # nothing to do here for draws

            # expected score factor by elo
            elodiff = min(ep.maxlogdistance, max(-ep.maxlogdistance,
                (float(ei.elo) - float(ej.elo)) * ep.logdistancefactor))
            scorefactor_elo = 1 / (1 + math.exp(-elodiff))

            # initial adjustment values, which we may modify with additional rules
            adjustmenti = scorefactor_real - scorefactor_elo
            adjustmentj = scorefactor_elo - scorefactor_real

            # log.debug("Player i: {0}".format(ei.player_id))
            # log.debug("Player i's K: {0}".format(ei.k))
            # log.debug("Player j: {0}".format(ej.player_id))
            # log.debug("Player j's K: {0}".format(ej.k))
            # log.debug("Scorefactor real: {0}".format(scorefactor_real))
            # log.debug("Scorefactor elo: {0}".format(scorefactor_elo))
            # log.debug("adjustment i: {0}".format(adjustmenti))
            # log.debug("adjustment j: {0}".format(adjustmentj))

            if scorefactor_elo > 0.5:
            # player i is expected to win
                if scorefactor_real > 0.5:
                # he DID win, so he should never lose points.
                    adjustmenti = max(0, adjustmenti)
                else:
                # he lost, but let's make it continuous (making him lose less points in the result)
                    adjustmenti = (2 * scorefactor_real - 1) * scorefactor_elo
            else:
            # player j is expected to win
                if scorefactor_real > 0.5:
                # he lost, but let's make it continuous (making him lose less points in the result)
                    adjustmentj = (1 - 2 * scorefactor_real) * (1 - scorefactor_elo)
                else:
                # he DID win, so he should never lose points.
                    adjustmentj = max(0, adjustmentj)

            eloadjust[ei.player_id] += adjustmenti
            eloadjust[ej.player_id] += adjustmentj

    elo_deltas = {}
    for pid in pids:
        old_elo = float(elos[pid].elo)
        new_elo = max(float(elos[pid].elo) + eloadjust[pid] * elos[pid].k * ep.global_K / float(len(elos) - 1), ep.floor)
        elo_deltas[pid] = new_elo - old_elo

        elos[pid].elo = new_elo
        elos[pid].games += 1
        elos[pid].update_dt = datetime.datetime.utcnow()

        log.debug("Setting Player {0}'s Elo delta to {1}. Elo is now {2} (was {3}).".format(pid, elo_deltas[pid], new_elo, old_elo))

    save_elo_deltas(game, session, elo_deltas)

    return elos


def save_elo_deltas(game, session, elo_deltas):
    """
    Saves the amount by which each player's Elo goes up or down
    in a given game in the PlayerGameStat row, allowing for scoreboard display.

    elo_deltas is a dictionary such that elo_deltas[player_id] is the elo_delta
    for that player_id.
    """
    pgstats = {}
    for pgstat in session.query(PlayerGameStat).\
            filter(PlayerGameStat.game_id == game.game_id).\
            all():
                pgstats[pgstat.player_id] = pgstat

    for pid in elo_deltas.keys():
        try:
            pgstats[pid].elo_delta = elo_deltas[pid]
            session.add(pgstats[pid])
        except:
            log.debug("Unable to save Elo delta value for player_id {0}".format(pid))


# parameters for K reduction
# this may be touched even if the DB already exists
KREDUCTION = KReduction(600, 120, 0.5, 0, 32, 0.2)

# parameters for chess elo
# only global_K may be touched even if the DB already exists
# we start at K=200, and fall to K=40 over the first 20 games
ELOPARMS = EloParms(global_K = 200)
