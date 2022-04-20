from scipy.stats import lognorm, norm
import matplotlib.pyplot as plt
import sys
import argparse
from scheduler import Scheduler, LLV_Scheduler, SJF
from job import Job, ValueFunction, DistType
from random import randint, choice

value_funcs = [ValueFunction("(0, 100), (360, 90), (720, 80), (1080, 70), (1440, 60), (1800, 50), (2160, 40), (2520, 30), (2880, 20), (3240, 10), (3600, -5)"),\
            ValueFunction("(0, 100), (1800, 50), (3600, -5)")]

for i in range(36):
    val = value_funcs[0].evaluate(i*80)
    print(f"Value at {i*80} is {val}")