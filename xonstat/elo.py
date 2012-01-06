import sys
import math
import random

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


# For team games where multiple scores and elos are at play, the elos
# must be adjusted according to their strength relative to the player
# in the next-lowest scoreboard position.
def update(elos, ep):
    for x in elos:
        if x.elo == None:
            x.elo = ep.initial
        x.eloadjust = 0
    if len(elos) < 2:
        return elos
    for i in xrange(0, len(elos)):
        ei = elos[i]
        for j in xrange(i+1, len(elos)):
            ej = elos[j]
            si = ei.score
            sj = ej.score

            # normalize scores
            ofs = min(0, si, sj)
            si -= ofs
            sj -= ofs
            if si + sj == 0:
                si, sj = 1, 1 # a draw

            # real score factor
            scorefactor_real = si / float(si + sj)

            # estimated score factor by elo
            elodiff = min(ep.maxlogdistance, max(-ep.maxlogdistance, (ei.elo - ej.elo) * ep.logdistancefactor))
            scorefactor_elo = 1 / (1 + math.exp(-elodiff))

            # how much adjustment is good?
            # scorefactor(elodiff) = 1 / (1 + e^(-elodiff * logdistancefactor))
            # elodiff(scorefactor) = -ln(1/scorefactor - 1) / logdistancefactor
            # elodiff'(scorefactor) = 1 / ((scorefactor) (1 - scorefactor) logdistancefactor)
            # elodiff'(scorefactor) >= 4 / logdistancefactor

            # adjust'(scorefactor) = K1 + K2

            # so we want:
            # K1 + K2 <= 4 / logdistancefactor <= elodiff'(scorefactor)
            # as we then don't overcompensate

            adjustment = scorefactor_real - scorefactor_elo
            ei.eloadjust += adjustment
            ej.eloadjust -= adjustment
    for x in elos:
        x.elo = max(x.elo + x.eloadjust * x.k * ep.global_K / float(len(elos) - 1), ep.floor)
        x.games += 1
    return elos


# parameters for K reduction
# this may be touched even if the DB already exists
KREDUCTION = KReduction(600, 120, 0.5, 0, 32, 0.2)

# parameters for chess elo
# only global_K may be touched even if the DB already exists
# we start at K=200, and fall to K=40 over the first 20 games
ELOPARMS = EloParms(global_K = 200)

