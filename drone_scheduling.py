from dataclasses import dataclass
import string
from matplotlib.colors import LogNorm
from scipy.stats import lognorm, norm
from math import exp
import matplotlib.pyplot as plt
import numpy as np
import sys
from enum import Enum
import re

class DistType(Enum):
    Normal = 0
    Log_norm = 1

class ValueFuncType(Enum):
    line = 0
    sections = 1

class ValueFunction:
    func = lambda x : x
    pairs = []
    val1 = 0 
    val2 = 0
    type : ValueFuncType

    def expectedValue(self, tc):
        #print("getting expected value")
        if(self.type == ValueFuncType.line):
            x_inter = -self.val2 / self.val1
            if(x_inter > tc):
                y = self.evaluate(tc)
                return 0.5*y*(x_inter - tc)
            else:
                return 0
        #This needs to be fixed doesn't give the exact answer 
        else:
            total_val = 0
            for i in range(len(self.pairs) - 1):
                if(self.pairs[i+1][0] < tc):
                    total_val += self.pairs[i][1] / (self.pairs[i+1][0] - self.pairs[i][0])
            return total_val

    def evaluate(self, x):
        if(self.type == ValueFuncType.sections):
            i = 1
            #print("Evaluating " + str(self.pairs))
            while(i < len(self.pairs)):
                if(self.pairs[i][0] > x):
                    break
                else:
                    i += 1
            return self.pairs[i-1][1]
        else:
            return max(self.val1 * x + self.val2,0)

    def __init__(self, string):
        #print("Parsing " + string)
        pairRegex = re.compile(r'\(([0-9]+),(\s*[0-9]+)\)')
        if(pairRegex.search(string)):
            self.type = ValueFuncType.sections 
            for pair in pairRegex.findall(string):
                self.pairs.append([int(pair[0]),int(pair[1])])
        else:
            self.type = ValueFuncType.line
            lineRegex1 = re.compile(r'(-?[0-9]+\.?[0-9]*)x\s*([\+,\-]\s*[0-9]+)') 
            lineRegex2 = re.compile(r'(-?[0-9]+)\s*([\+,\-]\s*[0-9]+\.?[0-9]*)x')   
            if(lineRegex1.search(string)):
                nums = lineRegex1.findall(string)
                self.val1 = float(nums[0][0].replace("+",""))
                self.val2 = float(nums[0][1].replace("+",""))
            elif(lineRegex2.search(string)):
                nums = lineRegex2.findall(string)
                self.val1 = float(nums[0][1].replace("+",""))
                self.val2 = float(nums[0][0].replace("+",""))
            else:
                print("ERROR ON " + string)
                4/0
            #print("{} + {}x".format(self.val1,self.val2))

@dataclass
class Job:
    id : int
    arrival_time : int
    dist_type : DistType
    duration_mean : int
    duration_sd : int
    value_function : ValueFunction
    penalty : int
    dependent_id : int

    duration_dist : norm = None
    NLV : float = -1
    started : int = -1

    #PLV is the potential lost value
    def PLV(self,jobs,tc):
        lostvalue = 0
        for job in jobs:
            if(job != self):
                lostvalue += job.EV(tc) - job.EV(tc + self.ED())
        return lostvalue
    
    #PGV is the potential gained value
    def PGV(self,tc):
        wonvalue = self.EV(tc) - self.EV(tc + self.ED())
        return tc

    #EV is the expected value of a job
    def EV(self, tc):
        return self.value_function.expectedValue(tc)

    #ED is the expected duration of a job
    def ED(self):
        return self.duration_dist.mean()

    def ED_inv(self,jobs):
        for job in jobs:
            if(job != self):
                tot_time += job.ED()
        return tot_time / (len(jobs) - 1)

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

class Scheduler:

    pending_jobs = []

    def add_job(self, job):
        self.pending_jobs.append(job)
    
    def get_next_job(self, time):
        return self.pending_jobs.pop(0)

    def has_pending(self):
        return len(self.pending_jobs) > 0

class LLV_Scheduler(Scheduler):

    def get_next_job(self, time):
        self.LLVJobSort(time)
        return self.pending_jobs.pop(0)

    def LLVJobSort(self, tc):
        for job in self.pending_jobs:
            job.NLV = job.PLV(self.pending_jobs, tc) - job.PGV(tc)
        self.pending_jobs.sort(key = lambda x : x.NLV)

class Simulation:

    scheduler : Scheduler
    incoming_jobs = []
    
    def __init__(self, jobs, scheduler):
        self.incoming_jobs = jobs
        self.incoming_jobs.sort(key = lambda x : x.arrival_time)
        self.scheduler = scheduler

    def Run(self):
        time = 0
        current_job = None
        total_value = 0
        while(len(self.incoming_jobs) > 0 or self.scheduler.has_pending() or current_job != None): #or len(pending_jobs) > 0):
            while(len(self.incoming_jobs) > 0 and self.incoming_jobs[0].arrival_time <= time):
                new_job = self.incoming_jobs.pop(0)
                #print(str(new_job.id) + " arrived at time " + str(time))
                self.scheduler.add_job(new_job)

            if(current_job == None):
                current_job = self.scheduler.get_next_job(time)
                current_job.started = time
            elif(time - current_job.started >= current_job.duration_mean):
                value_generated = current_job.value_function.evaluate(time - current_job.started)
                print("Job {} finished at time {} (took {}) value = {}".format(current_job.id, time, time - current_job.started, value_generated))
                total_value += value_generated
                current_job = None
            time += 1
        print("Total value generated is {:.2f}".format(total_value))

def main(argv):
    Jobs = ParseInputFile(argv[0])
    simulation = Simulation(Jobs, LLV_Scheduler() if len(argv) > 1 and argv[1] == 'LLV' else Scheduler())
    simulation.Run()

if __name__ == "__main__":
   main(sys.argv[1:])