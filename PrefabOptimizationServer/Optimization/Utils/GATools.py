import deap
from operator import attrgetter

# Roulette selection for minimization case with n bests for sure selected
def selMinRouletteWithNBests(individuals, k, nBests):
    s_inds = sorted(individuals, key=attrgetter("fitness"), reverse=True)
    fitnesses = []
    for ind in s_inds:
        fitnesses.append(ind.fitness.values[0])

    f_max = max(fitnesses)
    for i in range(len(fitnesses)):
        fitnesses[i] = f_max - fitnesses[i]

    sum_fits = sum(fitnesses)
    
    chosen = []
    for i in range(nBests):
        chosen.append(s_inds[i])
    for i in range(k - nBests):
        u = random.random() * sum_fits
        sum_ = 0
        for ind in s_inds:
            sum_ += f_max - ind.fitness.values[0]
            if sum_ > u:
                chosen.append(ind)
                break
    
    return chosen

class varInterval:
    def __init__(self, minVal, maxVal):
        self.min = minVal
        self.max = maxVal

    def isInInterval(self, val):
        return val <= self.max and val >= self.min

class varLambdaInterval:
    def __init__(self, predicate):
        self.predicate = predicate

    def isInInterval(self, val):
        return self.predicate(val)
