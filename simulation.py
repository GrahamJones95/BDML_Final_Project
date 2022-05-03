from scipy.stats import norm
from math import sqrt, sin, cos
from scheduler import Scheduler
from job import Job, ValueFunction, DistType
from random import randint, choice, random

class Simulation:
    
    def __init__(self, scheduler):
        self.scheduler : Scheduler = scheduler 
        self.max_time = 6*60*60 #6 hours per the paper

    def Run(self, arrival_interval = 60, queue_size = 40, num_drones = 15):
        time = 0
        job_gen : Job_Generator = Job_Generator(arrival_interval)
        job_queue : ActiveDrones = ActiveDrones(num_drones)

        #Telemetry saving
        total_value = 0
        value_array = []
        queue_length_hist = []
        number_deliveries = 0
        number_delivered_hist = []
        rev_per_delivery = []

        while(time < 6*60*60): #Each timestep corresponds to a second

            if(job_gen.new_job_available(time) and len(self.scheduler.pending_jobs) < queue_size):
                self.scheduler.add_job(job_gen.fetch_new_job(time))

            while(job_queue.droneIsAvailable() and self.scheduler.has_pending()):
                new_jobs = self.scheduler.get_next_job(time)
                for job in new_jobs:
                    job.started = time
                job_queue.current_jobs.append(Route(new_jobs, time))
            
            total_value -= job_queue.getNumberExpired(time)*5
            
            for route in job_queue.getFinishedJobs(time):
                value_generated = route.get_value(time)
                #print("Job {} finished at time {} (took {}) value = {} Queue size = {}".format(route.Jobs[0].id, time, time - route.Jobs[0].started, value_generated,len(self.scheduler.pending_jobs)))
                total_value += value_generated
                number_deliveries += len(route.Jobs)

            time += 1
            value_array.append(total_value)
            queue_length_hist.append(len(self.scheduler.pending_jobs))
            number_delivered_hist.append(number_deliveries)
            rev_per_delivery.append( 0 if(number_deliveries == 0) else total_value / number_deliveries)
            
        #print("Total value generated is {:.2f}".format(total_value))
        return value_array, queue_length_hist, number_delivered_hist, rev_per_delivery

class ActiveDrones:

    def __init__(self, number_drones) -> None:
        self.num_drones : int = number_drones
        self.current_jobs : list[Route] = []

    def droneIsAvailable(self):
        return len(self.current_jobs) < self.num_drones

    def getFinishedJobs(self, tc):
        finished_jobs = []
        for route in self.current_jobs:
            if(route.is_finished(tc)):
                finished_jobs.append(route)
                self.current_jobs.remove(route)
        return finished_jobs
    
    def getNumberExpired(self, tc):
        count = 0
        for route in self.current_jobs:
            for job in route.Jobs:
                if(not job.expired and tc - job.arrival_time >= 60):
                    count += 1
                    job.expired = True
        return count
                

class Drone:

    charge_time : int = 2

    def __init__(self, max_range) -> None:
        self.jobs : list[Job] = []
        self.max_range : int = max_range
        self.rem_range : int = max_range
    
    def recharge(self) -> int:
        time_to_charge = (self.max_range - self.rem_range)*time_to_charge
        self.rem_range = self.max_range
        return time_to_charge

class Job_Generator:

    MAX_DIST = 900 #Must be less than 1800 to complete in an hour
    MIN_DIST = 0

    def __init__(self, interval) -> None:
        self.time_interval = interval
        self.job_num = 0
        self.value_funcs = [ValueFunction("(0, 100), (360, 90), (720, 80), (1080, 70), (1440, 60), (1800, 50), (2160, 40), (2520, 30), (2880, 20), (3240, 10), (3600, 0)"),\
            ValueFunction("(0, 100), (1800, 50), (3600, 0)")]
    
    def new_job_available(self, tc) -> bool:
        if(tc % self.time_interval == 0):
            return True
        else:
            return False

    def fetch_new_job(self, tc) -> Job:
        r = (self.MAX_DIST - self.MIN_DIST) * sqrt(random()) + self.MIN_DIST
        theta = random() * 2 * 3.1415

        x = r * cos(theta)
        y = r * sin(theta)

        job = Job(self.job_num, tc, choice(self.value_funcs), (x,y))
        self.job_num += 1
        return job

class Route:

    def __init__(self) -> None:
        self.Jobs : list[Job] = []
    
    def __init__(self, jobs : list[Job], tc) -> None:
        self.Jobs = jobs
        self.start_time = tc
        self.end_time = tc + self.get_duration()

    def get_value(self, tc) -> int:
        total_val = 0
        gap = self.Jobs[-1].get_duration()
        for i,job in reversed(list(enumerate(self.Jobs))):
            total_val += job.value_function.evaluate((tc - gap) - job.arrival_time)
            gap += self.Jobs[i].get_duration(self.Jobs[i-1].location)
        return total_val
    
    def get_duration(self):
        tot_duration = 0
        tot_duration += self.Jobs[0].get_duration()
        for i in range(1,len(self.Jobs)):
            tot_duration +=  self.Jobs[i].get_duration(self.Jobs[i - 1].location)
        
        tot_duration += self.Jobs[-1].get_duration()
        return tot_duration

    def is_finished(self, tc):
        return tc >= self.end_time
