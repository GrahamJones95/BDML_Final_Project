#Continuous is just a copy of the main file, but with adaptations to allow for continuously streaming inputs

from dataclasses import dataclass
from random import Random
from matplotlib.colors import LogNorm
from scipy.stats import lognorm, norm
from math import exp
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse
from scheduler import Scheduler, LLV_Scheduler, SJF
from job import Job, ValueFunction, DistType
from random import randint, choice

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

class Simulation:
    
    def __init__(self, scheduler):
        self.scheduler : Scheduler = scheduler      

    def Run(self):
        time = 0
        current_job = None
        total_value = 0
        value_array = []
        job_queue = []
        job_num = 0
        value_funcs = [ValueFunction("(0, 100), (360, 90), (720, 80), (1080, 70), (1440, 60), (1800, 50), (2160, 40), (2520, 30), (2880, 20), (3240, 10), (3600, -5)"),\
            ValueFunction("(0, 100), (1800, 50), (3600, -5)")]
        while(time < 6*60*60): #Each timestep corresponds to a second

            if(time % (30*6) == 0):
                rand_duration = randint(100,500)
                job = Job(job_num, time, DistType.Normal, rand_duration,0,choice(value_funcs),-1,-1,norm(rand_duration))
                self.scheduler.add_job(job)
                job_num += 1

            if(current_job == None and self.scheduler.has_pending()):
                current_job = self.scheduler.get_next_job(time)
                current_job.started = time
            elif(current_job != None and time - current_job.started >= current_job.duration_mean):
                value_generated = current_job.value_function.evaluate(time - current_job.arrival_time)
                print("Job {} finished at time {} (took {}) value = {} Queue size = {}".format(current_job.id, time, time - current_job.started, value_generated,len(self.scheduler.pending_jobs)))
                total_value += value_generated
                current_job = None
            time += 1
            value_array.append(total_value)
            job_queue.append(len(self.scheduler.pending_jobs))
        print("Total value generated is {:.2f}".format(total_value))
        return value_array,job_queue

#Delete this late, this function is just for examining the value functions of individuals jobs
#was used for debugging issues with the expected value function
def examineJob(job):
    print(job.value_function.type)
    print("y = {}x + {}".format(job.value_function.slope,job.value_function.intercept))
    for i in range(12):
        print("Job {} expected value at {} is {}".format(job.id,i*100,job.value_function.expectedValue(i*100)))


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file',type=str)
    parser.add_argument('--sched', dest='sched',choices=["LLV","FCFS","SJF"])

    #args = parser.parse_args()

    #print(args.input_file)

    #Jobs = ParseInputFile(args.input_file)
    
    f, (ax1, ax2) = plt.subplots(2)
    ax1.set_title("Profit over time")
    ax2.set_title("Queue size over time")

    for scheduler in [(Scheduler(),"FCFS"),(LLV_Scheduler(),"LLV"),(SJF(),"SJF")]: 
        simulation = Simulation(scheduler[0])
        profit,queue = simulation.Run()
        ax1.plot(profit, label=scheduler[1])
        ax2.plot(queue, label=scheduler[1])

    ax1.legend()
    ax2.legend()
    plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])