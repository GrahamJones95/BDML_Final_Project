from scipy.stats import norm
from math import sqrt
from scheduler import Scheduler
from job import Job, ValueFunction, DistType
from random import randint, choice

class Simulation:
    
    def __init__(self, scheduler):
        self.scheduler : Scheduler = scheduler 
        self.max_time = 6*60*60 #6 hours per the paper

    def Run(self):
        time = 0
        num_drones : int = 5
        job_gen : Job_Generator = Job_Generator(60)
        job_queue : ActiveJobs = ActiveJobs(num_drones)

        #Telemetry saving
        total_value = 0
        value_array = []
        queue_length_hist = []
        number_deliveries = 0
        number_delivered_hist = []
        rev_per_delivery = []

        while(time < 6*60*60): #Each timestep corresponds to a second

            if(job_gen.new_job_available(time)):
                self.scheduler.add_job(job_gen.fetch_new_job(time))

            if(job_queue.droneIsAvailable() and self.scheduler.has_pending()):
                new_job = self.scheduler.get_next_job(time)
                new_job.started = time
                job_queue.current_jobs.append(new_job)
            
            for job in job_queue.getFinishedJobs(time):
                value_generated = job.value_function.evaluate(time - job.arrival_time)
                print("Job {} finished at time {} (took {}) value = {} Queue size = {}".format(job.id, time, time - job.started, value_generated,len(self.scheduler.pending_jobs)))
                total_value += value_generated
                number_deliveries += 1

            time += 1
            value_array.append(total_value)
            queue_length_hist.append(len(self.scheduler.pending_jobs))
            number_delivered_hist.append(number_deliveries)
            rev_per_delivery.append( 0 if(number_deliveries == 0) else total_value / number_deliveries)
            
        print("Total value generated is {:.2f}".format(total_value))
        return value_array, queue_length_hist, number_delivered_hist, rev_per_delivery

class ActiveJobs:

    def __init__(self, number_drones) -> None:
        self.num_drones : int = number_drones
        self.current_jobs : list[Job] = []

    def droneIsAvailable(self):
        return len(self.current_jobs) < self.num_drones

    def getFinishedJobs(self, tc):
        finished_jobs = []
        for job in self.current_jobs:
            if(tc - job.started >= job.end_time):
                finished_jobs.append(job)
                self.current_jobs.remove(job)
        return finished_jobs
                

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

    def __init__(self, interval) -> None:
        self.time_interval = interval
        self.job_num = 0
        self.value_funcs = [ValueFunction("(0, 100), (360, 90), (720, 80), (1080, 70), (1440, 60), (1800, 50), (2160, 40), (2520, 30), (2880, 20), (3240, 10), (3600, -5)"),\
            ValueFunction("(0, 100), (1800, 50), (3600, -5)")]
    
    def new_job_available(self, tc) -> bool:
        if(tc % self.time_interval == 0):
            return True
        else:
            return False

    def fetch_new_job(self, tc) -> Job:
        rand_duration = sqrt(randint(10000,250000))
        sigma = 10
        job = Job(self.job_num, tc, DistType.Normal, rand_duration, sigma, choice(self.value_funcs), -1, -1, norm(rand_duration))
        job.end_time = job.duration_dist.rvs(1)
        self.job_num += 1
        return job
