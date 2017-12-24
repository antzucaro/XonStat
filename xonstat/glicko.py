import logging
import math
import sys

from xonstat.models import PlayerGlicko, Game, PlayerGameStat

log = logging.getLogger(__name__)

# DEBUG
# log.addHandler(logging.StreamHandler())
# log.setLevel(logging.DEBUG)

# the default system volatility constant
TAU = 0.3

# how much ping influences results
LATENCY_TREND_FACTOR = 0.2


def calc_g(phi):
    return 1 / math.sqrt(1 + (3 * phi ** 2) / (math.pi ** 2))


def calc_e(mu, mu_j, phi_j):
    return 1. / (1 + math.exp(-calc_g(phi_j) * (mu - mu_j)))


def calc_v(gs, es):
    """ Estimated variance of the team or player's ratings based only on game outcomes. """
    total = 0.0
    for i in range(len(gs)):
        total += (gs[i] ** 2) * es[i] * (1-es[i])

    return 1. / total


def calc_delta(v, gs, es, results):
    """
    Compute the estimated improvement in rating by comparing the pre-period rating to the
    performance rating based only on game outcomes.
    """
    total = 0.0
    for i in range(len(gs)):
        total += gs[i] * (results[i] - es[i])

    return v * total


def calc_sigma_bar(sigma, delta, phi, v, tau=TAU):
    """ Compute the new volatility. """
    epsilon = 0.000001
    A = a = math.log(sigma**2)

    # pre-compute some terms
    delta_sq = delta ** 2
    phi_sq = phi ** 2

    def f(x):
        e_up_x = math.e ** x
        term_a = (e_up_x * (delta_sq - phi_sq - v - e_up_x)) / (2 * (phi_sq + v + e_up_x) ** 2)
        term_b = (x - a) / tau ** 2
        return term_a - term_b

    if delta_sq > (phi_sq + v):
        B = math.log(delta_sq - phi_sq - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        B = a - k * tau

    fa, fb = f(A), f(B)
    while abs(B - A) > epsilon:
        C = A + (A - B) * (fa / (fb - fa))
        fc = f(C)

        if fc * fb < 0:
            A, fa = B, fb
        else:
            fa /= 2

        B, fb = C, fc

        # DEBUG
        # log.debug("A={}, B={}, C={}, fA={}, fB={}, fC={}".format(A, B, C, fa, fb, fc))

    return math.e ** (A / 2)


def rate(player, opponents, results):
    """
    Calculate the ratings improvement for a given player, provided their opponents and
    corresponding results versus them.
    """
    if len(opponents) == 0 or len(results) == 0:
        return player

    p_g2 = player.to_glicko2()

    gs = []
    es = []
    for i in range(len(opponents)):
        o_g2 = opponents[i].to_glicko2()
        gs.append(calc_g(o_g2.phi))
        es.append(calc_e(p_g2.mu, o_g2.mu, o_g2.phi))

        # DEBUG
        # log.debug("j={} muj={} phij={} g={} e={} s={}"
                  # .format(i+1, o_g2.mu, o_g2.phi, gs[i], es[i], results[i]))

    v = calc_v(gs, es)
    delta = calc_delta(v, gs, es, results)
    sigma_bar = calc_sigma_bar(p_g2.sigma, delta, p_g2.phi, v)

    phi_tmp = math.sqrt(p_g2.phi ** 2 + sigma_bar ** 2)
    phi_bar = 1/math.sqrt((1/phi_tmp**2) + (1/v))

    sum_terms = 0.0
    for i in range(len(opponents)):
        sum_terms += gs[i] * (results[i] - es[i])

    mu_bar = p_g2.mu + phi_bar**2 * sum_terms

    new_rating = PlayerGlicko(player.player_id, player.game_type_cd, player.category, mu_bar,
                              phi_bar, sigma_bar).from_glicko2()

    # DEBUG
    # log.debug("v={}".format(v))
    # log.debug("delta={}".format(delta))
    # log.debug("sigma_temp={}".format(sigma_temp))
    # log.debug("sigma_bar={}".format(sigma_bar))
    # log.debug("phi_bar={}".format(phi_bar))
    # log.debug("mu_bar={}".format(mu_bar))
    # log.debug("new_rating: {} {} {}".format(new_rating.mu, new_rating.phi, new_rating.sigma))

    return new_rating


class KReduction:
    """
    Scale the points gained or lost for players based on time played in the given game.
    """
    def __init__(self, full_time=600, min_time=120, min_ratio=0.5):
        # full time is the time played to count the player in a game
        self.full_time = full_time

        # min time is the time played to count the player at all in a game
        self.min_time = min_time

        # min_ratio is the ratio of the game's time to be played to be counted fully (provided
        # they went past `full_time` and `min_time` above.
        self.min_ratio = min_ratio

    def eval(self, my_time, match_time):
        # kick out players who didn't play enough of the match
        if my_time < self.min_time:
            return 0.0

        if my_time < self.min_ratio * match_time:
            return 0.0

        # scale based on time played versus what is defined as `full_time`
        if my_time < self.full_time:
            k = my_time / float(self.full_time)
        else:
            k = 1.0

        return k


# Parameters for reduction of points
KREDUCTION = KReduction()


class GlickoWIP(object):
    """ A work-in-progress Glicko value. """
    def __init__(self, pg):
        """
        Initialize a GlickoWIP instance.
        :param pg: the player's PlayerGlicko record.
        """
        # the player's current (or base) PlayerGlicko record
        self.pg = pg

        # the list of k factors for each game in the ranking period
        self.k_factors = []

        # the list of ping factors for each game in the ranking period
        self.ping_factors = []

        # the list of opponents (PlayerGlicko or PlayerGlickoBase) in the ranking period
        self.opponents = []

        # the list of results for those games in the ranking period
        self.results = []


class GlickoProcessor(object):
    """
    Processes an arbitrary list games using the Glicko2 algorithm.
    """
    def __init__(self, session):
        """
        Create a GlickoProcessor instance.

        :param session: the SQLAlchemy session to use for fetching/saving records.
        """
        self.session = session
        self.wips = {}

    def _pingratio(self, pi, pj):
        """
        Calculate the ping differences between the two players, but only if both have them.

        :param pi: the latency of player I
        :param pj: the latency of player J
        :return: float
        """
        if pi is None or pj is None or pi < 0 or pj < 0:
            # default to a draw
            return 0.5

        else:
            return float(pi)/(pi+pj)

    def _load_game(self, game_id):
        try:
            game = self.session.query(Game).filter(Game.game_id==game_id).one()
            return game
        except Exception as e:
            log.error("Game ID {} not found.".format(game_id))
            log.error(e)
            raise e

    def _load_pgstats(self, game):
        """
        Retrieve the game stats from the database for the game in question.

        :param game: the game record whose player stats will be retrieved
        :return: list of PlayerGameStat
        """
        try:
            pgstats_raw = self.session.query(PlayerGameStat)\
                .filter(PlayerGameStat.game_id==game.game_id)\
                .filter(PlayerGameStat.player_id > 2)\
                .all()

            return pgstats_raw

        except Exception as e:
            log.error("Error fetching player_game_stat records for game {}".format(game.game_id))
            log.error(e)
            raise e

    def _filter_pgstats(self, game, pgstats_raw):
        """
        Filter the raw game stats so that all of them are Glicko-eligible.

        :param pgstats_raw: the list of raw PlayerGameStat
        :return: list of PlayerGameStat
        """
        pgstats = []
        for pgstat in pgstats_raw:
            # ensure warmup isn't included in the pgstat records
            if pgstat.alivetime > game.duration:
                pgstat.alivetime = game.duration

            # ensure players played enough of the match to be included
            k = KREDUCTION.eval(pgstat.alivetime.total_seconds(), game.duration.total_seconds())
            if k <= 0.0:
                continue
            elif pgstat.player_id <= 2:
                continue
            else:
                pgstats.append(pgstat)

        return pgstats

    def _load_glicko_wip(self, player_id, game_type_cd, category):
        """
        Retrieve a PlayerGlicko record from the database or local cache.

        :param player_id: the player ID to fetch
        :param game_type_cd: the game type code
        :param category: the category of glicko to retrieve
        :return: PlayerGlicko
        """
        if (player_id, game_type_cd, category) in self.wips:
            return self.wips[(player_id, game_type_cd, category)]

        try:
            pg = self.session.query(PlayerGlicko)\
                     .filter(PlayerGlicko.player_id==player_id)\
                     .filter(PlayerGlicko.game_type_cd==game_type_cd)\
                     .filter(PlayerGlicko.category==category)\
                     .one()

        except:
            pg = PlayerGlicko(player_id, game_type_cd, category)

        # cache this in the wips dict
        wip = GlickoWIP(pg)
        self.wips[(player_id, game_type_cd, category)] = wip

        return wip

    def load(self, game_id, game=None, pgstats=None):
        """
        Load all of the needed information from the database. Compute results for each player pair.
        """
        if game is None:
            game = self._load_game(game_id)

        if pgstats is None:
            pgstats = self._load_pgstats(game)

        pgstats = self._filter_pgstats(game, pgstats)

        game_type_cd = game.game_type_cd
        category = game.category

        # calculate results:
        #   wipi/j => work in progress record for player i/j
        #   ki/j   => k reduction value for player i/j
        #   si/j   => score per second for player i/j
        #   pi/j   => ping ratio for player i/j
        for i in xrange(0, len(pgstats)):
            wipi = self._load_glicko_wip(pgstats[i].player_id, game_type_cd, category)
            ki = KREDUCTION.eval(pgstats[i].alivetime.total_seconds(),
                                 game.duration.total_seconds())
            si = pgstats[i].score/float(game.duration.total_seconds())

            for j in xrange(i+1, len(pgstats)):
                # ping factor is opponent-specific
                pi = self._pingratio(pgstats[i].avg_latency, pgstats[j].avg_latency)
                pj = 1.0 - pi

                wipj = self._load_glicko_wip(pgstats[j].player_id, game_type_cd, category)
                kj = KREDUCTION.eval(pgstats[j].alivetime.total_seconds(),
                                     game.duration.total_seconds())
                sj = pgstats[j].score/float(game.duration.seconds)

                # normalize scores
                ofs = min(0.0, si, sj)
                si -= ofs
                sj -= ofs
                if si + sj == 0:
                    si, sj = 1, 1 # a draw

                scorefactor_i = si / float(si + sj)
                scorefactor_j = 1.0 - si

                wipi.k_factors.append(ki)
                wipi.ping_factors.append(pi)
                wipi.opponents.append(wipj.pg)
                wipi.results.append(scorefactor_i)

                wipj.k_factors.append(kj)
                wipj.ping_factors.append(pj)
                wipj.opponents.append(wipi.pg)
                wipj.results.append(scorefactor_j)

    def process(self):
        """
        Calculate the Glicko2 ratings, deviations, and volatility updates for the records loaded.
        """
        for wip in self.wips.values():
            new_pg = rate(wip.pg, wip.opponents, wip.results)

            log.debug("New rating for player {} before factors: mu={} phi={} sigma={}"
                      .format(new_pg.player_id, new_pg.mu, new_pg.phi, new_pg.sigma))

            avg_k_factor = sum(wip.k_factors)/len(wip.k_factors)
            avg_ping_factor = LATENCY_TREND_FACTOR * sum(wip.ping_factors)/len(wip.ping_factors)

            points_delta = (new_pg.mu - wip.pg.mu) * avg_k_factor * avg_ping_factor

            wip.pg.mu += points_delta
            wip.pg.phi = new_pg.phi
            wip.pg.sigma = new_pg.sigma

            log.debug("New rating for player {} after factors: mu={} phi={} sigma={}"
                      .format(wip.pg.player_id, wip.pg.mu, wip.pg.phi, wip.pg.sigma))

    def save(self):
        """
        Put all changed PlayerElo and PlayerGameStat instances into the
        session to be updated or inserted upon commit.
        """
        for wip in self.wips.values():
            self.session.add(wip.pg)

        self.session.commit()


def main():
    # the example in the actual Glicko2 paper, for verification purposes
    pA = PlayerGlicko(1, "duel", mu=1500, phi=200)
    pB = PlayerGlicko(2, "duel", mu=1400, phi=30)
    pC = PlayerGlicko(3, "duel", mu=1550, phi=100)
    pD = PlayerGlicko(4, "duel", mu=1700, phi=300)

    opponents = [pB, pC, pD]
    results = [1, 0, 0]

    rate(pA, opponents, results)


if __name__ == "__main__":
     sys.exit(main())
