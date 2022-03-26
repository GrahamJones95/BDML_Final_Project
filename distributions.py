from scipy.stats import lognorm, norm

from math import exp, log
import matplotlib.pyplot as plt
import numpy as np

my_dist = norm(10,)


print(norm(10).expect(lambda x : x))
print(lognorm(10, 10).expect(lambda x : x, ub = 100000000, lb = 0))
print(exp(10 + 1/2))

dist = lognorm(343, scale = log(5532)-(343*343)/2)

print(dist.expect(lambda x : x))