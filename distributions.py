from scipy.stats import lognorm, norm

from math import exp
import matplotlib.pyplot as plt
import numpy as np

my_dist = norm(10,)


print(norm(10).expect(lambda x : x))
print(lognorm(s = 1, scale = exp(100)).expect(lambda x : x, ub = 100000000, lb = 0))