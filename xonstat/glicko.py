import logging
import math

log = logging.getLogger(__name__)

# the default initial rating value
MU = 1500

# the default ratings deviation value
PHI = 350

# the default volatility value
SIGMA = 0.06

# the default system volatility constant
TAU = 0.3

# the ratio to convert from/to glicko2
GLICKO2_SCALE = 173.7178


class PlayerGlicko(object):
    def __init__(self, mu=MU, phi=PHI, sigma=SIGMA):
        self.mu = mu
        self.phi = phi
        self.sigma = sigma

    def to_glicko2(self):
        """ Convert a rating to the Glicko2 scale. """
        return PlayerGlicko(
            mu=(self.mu - MU) / GLICKO2_SCALE,
            phi=self.phi / GLICKO2_SCALE,
            sigma=self.sigma
        )

    def from_glicko2(self):
        """ Convert a rating to the original Glicko scale. """
        return PlayerGlicko(
            mu=self.mu * GLICKO2_SCALE + MU,
            phi=self.phi * GLICKO2_SCALE,
            sigma=self.sigma
        )


def g(phi):
    return 1 / math.sqrt(1 + (3 * phi ** 2) / (math.pi ** 2))


def e(mu, mu_j, phi_j):
    return 1. / (1 + math.exp(-g(phi_j) * (mu - mu_j)))


def v(gs, es):
    """ Estimated variance of the team or player's ratings based only on game outcomes. """
    total = 0.0
    for i in range(len(gs)):
        total += (gs[i] ** 2) * es[i] * (1-es[i])

    return 1. / total


def delta(v, gs, es, results):
    """ Compute the estimated improvement in rating by comparing the pre-period rating to the
    performance rating based only on game outcomes. """
    total = 0.0
    for i in range(len(gs)):
        total += gs[i] * (results[i] - es[i])

    return v * total
