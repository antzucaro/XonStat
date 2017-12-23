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
        self.ks = []

        # the list of opponents (PlayerGlicko or PlayerGlickoBase) in the ranking period
        self.opponents = []

        # the list of results for those games in the ranking period
        self.results = []


class GlickoProcessor(object):
    """
    Processes the given list games using the Glicko2 algorithm.
    """
    def __init__(self, session):
        """
        Create a GlickoProcessor instance.

        :param session: the SQLAlchemy session to use for fetching/saving records.
        :param game_ids: the list of game_ids that need to be processed.
        """
        self.session = session
        self.wips = {}

    def scorefactor(self, si, sj, game_type_cd):
        """
        Calculate the real scorefactor of the game. This is how players
        actually performed, which is compared to their expected performance.

        :param si: the score per second of player I
        :param sj: the score per second of player J
        :param game_type_cd: the game type of the game in question
        :return: float
        """
        scorefactor_real = si / float(si + sj)

        # duels are done traditionally - a win nets
        # full points, not the score factor
        if game_type_cd == 'duel':
            # player i won
            if scorefactor_real > 0.5:
                scorefactor_real = 1.0
            # player j won
            elif scorefactor_real < 0.5:
                scorefactor_real = 0.0
            # nothing to do here for draws

        return scorefactor_real

    def pingfactor(self, pi, pj):
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

    def load(self, game_id):
        """
        Load all of the needed information from the database.
        """
        try:
            game = self.session.query(Game).filter(Game.game_id==game_id).one()
        except:
            log.error("Game ID {} not found.".format(game_id))
            return

        try:
            pgstats_raw = self.session.query(PlayerGameStat)\
                .filter(PlayerGameStat.game_id==game_id)\
                .filter(PlayerGameStat.player_id > 2)\
                .all()

            # ensure warmup isn't included in the pgstat records
            for pgstat in pgstats_raw:
                if pgstat.alivetime > game.duration:
                    pgstat.alivetime = game.duration
        except:
            log.error("Error fetching player_game_stat records for game {}".format(self.game_id))
            return

    def process(self):
        """
        Calculate the Glicko2 ratings, deviations, and volatility updates for the records loaded.
        :return: bool
        """
        pass

    def save(self, session):
        """
        Put all changed PlayerElo and PlayerGameStat instances into the
        session to be updated or inserted upon commit.
        """
        pass


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
