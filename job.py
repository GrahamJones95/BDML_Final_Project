from enum import Enum
import re
from dataclasses import dataclass
from scipy.stats import lognorm, norm

class DistType(Enum):
    Normal = 0
    Log_norm = 1

class ValueFuncType(Enum):
    line = 0
    sections = 1

class ValueFunction:
    #Note that currently the line type does not work for penalties
    def expectedValue(self, tc):
        if(self.type == ValueFuncType.line):
            x_inter = -self.intercept / self.slope
            if(x_inter > tc):
                return self.evaluate((x_inter - tc)/2)
            else:
                return 0
        else:
            total_val = 0
            start = self.pairs[-1][0]
            for i in range(len(self.pairs) - 1):
                if(self.pairs[i+1][0] > tc):
                    if(self.pairs[i][0] <= tc):
                        start = tc
                        total_val += self.pairs[i][1] * (self.pairs[i+1][0] - tc)
                    else:
                        total_val += self.pairs[i][1] * (self.pairs[i+1][0] - self.pairs[i][0])
            if(start < self.pairs[-1][0]):
                return total_val / (self.pairs[-1][0] - start)
            else:
                return self.pairs[-1][1]

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
            return max(self.slope * x + self.intercept,0)

    def __init__(self, string):
        self.func = lambda x : x
        self.pairs = []
        self.slope = 0 
        self.intercept = 0
        self.type : ValueFuncType
        print("Parsing " + string)
        pairRegex = re.compile(r'\(([0-9]+),(\s*-?[0-9]+)\)')
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
                self.slope = float(nums[0][0].replace("+",""))
                self.intercept = float(nums[0][1].replace("+",""))
            elif(lineRegex2.search(string)):
                nums = lineRegex2.findall(string)
                self.slope = float(nums[0][1].replace("+",""))
                self.intercept = float(nums[0][0].replace("+",""))
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
                lostvalue += (job.EV(tc) - job.EV(tc + self.ED()))
        return lostvalue
    
    #PGV is the potential gained value
    def PGV(self,tc,jobs):
        wonvalue = self.EV(tc) - self.EV(tc + self.ED_avg(jobs))
        return wonvalue

    #EV is the expected value of a job
    def EV(self, tc):
        return self.value_function.expectedValue(tc - self.arrival_time)

    #ED is the expected duration of a job
    def ED(self):
        return self.duration_dist.mean()
        #return self.duration_mean

    def ED_avg(self,jobs):
        tot_time = 0
        if(len(jobs) == 1):
            return 0
        for job in jobs:
            if(job != self):
                tot_time += job.ED()
        return tot_time / (len(jobs) - 1)