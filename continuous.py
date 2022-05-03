#Continuous is just a copy of the main file, but with adaptations to allow for continuously streaming inputs

from scipy.stats import lognorm, norm
from math import sqrt
import matplotlib.pyplot as plt
import sys
import argparse
from scheduler import SJF_Multi, Scheduler, LLV_Scheduler, SJF, FCFS_Multi
from job import Job, ValueFunction, DistType
from random import randint, choice
from simulation import Simulation

def ParseInputFile(filename):
    input_file = open(filename,'r')
    input_file.readline()
    Jobs = []
    for line in input_file:
        params = line.split("\t")
        id = int(params[0])
        arrival_time = int(params[1])
        dist_type = DistType.Log_norm if params[2] == "LOGNORMAL" else DistType.Normal
        duration_mean = int(params[3])
        duration_sd = int(params[4])
        value_function = ValueFunction(params[5])
        penalty = int(params[6])
        dependent_id = int(params[7])

        new_job = Job(id, arrival_time, dist_type, duration_mean, duration_sd, value_function, penalty, dependent_id)
        new_job.duration_dist = norm(loc = duration_mean, scale = duration_sd)
        Jobs.append(new_job)
    return Jobs


#Delete this late, this function is just for examining the value functions of individuals jobs
#was used for debugging issues with the expected value function
def examineJob(job):
    print(job.value_function.type)
    print("y = {}x + {}".format(job.value_function.slope,job.value_function.intercept))
    for i in range(12):
        print("Job {} expected value at {} is {}".format(job.id,i*100,job.value_function.expectedValue(i*100)))


def main(argv):
    run_experiment_1()
    #run_experiment_2()


def run_experiment_1():
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
    ax1.set_title("Profit over time")
    ax2.set_title("Queue size over time")
    ax3.set_title("Number of deliveries")
    ax4.set_title("Revenue per delivery")

    #schedulers = [(Scheduler(),"FCFS"),(LLV_Scheduler(),"LLV"),(SJF(),"SJF"),(FCFS_Multi(),"FCFS Multiple")]
    schedulers = [(Scheduler(),"FCFS"),(LLV_Scheduler(),"LLV"),(SJF(),"SJF"),(FCFS_Multi(),"FCFS Multiple"),(SJF_Multi(),"SJF Multiple")]
    #schedulers = [(FCFS_Multi(),"FCFS")]

    for scheduler in schedulers: 
        print(f"Running sim with {scheduler[1]}")
        simulation = Simulation(scheduler[0])
        profit, queue, number_deliveries, rev_per = simulation.Run()
        ax1.plot(profit, label=scheduler[1])
        ax2.plot(queue, label=scheduler[1])
        ax3.plot(number_deliveries, label=scheduler[1])
        ax4.plot(rev_per, label=scheduler[1])

    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    plt.show()

def run_experiment_2():
    plt.title("Total Profit vs Arrival Interval")
    plt.xlabel("Arrival Interval (s)")
    plt.ylabel("Profit")

    schedulers = [(Scheduler(),"FCFS"),(SJF(),"SJF"),(FCFS_Multi(),"FCFS Multiple"),(SJF_Multi(),"SJF Multiple")]
    #schedulers = [(Scheduler(),"FCFS"),(LLV_Scheduler(),"LLV"),(SJF(),"SJF"),(FCFS_Multi(),"FCFS Multiple"),(SJF_Multi(),"SJF Multiple")]
    #schedulers = [(FCFS_Multi(),"FCFS")]

    arrival_rates = range(50,301,5)
    for scheduler in schedulers: 
        profit_list = []
        simulation = Simulation(scheduler[0])
        for arrival_rate in arrival_rates:
            print(f"Running sim with {scheduler[1]}")
            profit, queue, number_deliveries, rev_per = simulation.Run(arrival_rate)
            profit_list.append(profit[-1])
        plt.plot(arrival_rates, profit_list, label=scheduler[1])

    plt.legend()
    plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])