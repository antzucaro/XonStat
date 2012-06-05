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


# parameters for K reduction
# this may be touched even if the DB already exists
KREDUCTION = KReduction(600, 120, 0.5, 0, 32, 0.2)

# parameters for chess elo
# only global_K may be touched even if the DB already exists
# we start at K=200, and fall to K=40 over the first 20 games
ELOPARMS = EloParms(global_K = 200)
