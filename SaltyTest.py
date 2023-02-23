import math 
from statistics import NormalDist

def probability_of_p1_win(p1mu = 29.39583201999916, p1sigma = 7.171475587326195, p2mu = 20.604167980000835, p2sigma = 7.171475587326195):
    prob_P1 = None
    deltaMu = (p1mu - p2mu)                   
    sumSigma = (p1sigma**2) + (p2sigma**2)  
    playerCount = 2                                               
    denominator = math.sqrt(playerCount * (4.166666666666667 * 4.166666666666667) + sumSigma)   
    prob_P1 = NormalDist().cdf(deltaMu/denominator)
    print(NormalDist().cdf(deltaMu/denominator))
    return prob_P1

probability_of_p1_win()
