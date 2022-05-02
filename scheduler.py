from job import Job

class Scheduler:

    DRONE_RANGE = 3600

    def __init__(self):
        self.pending_jobs = []

    def add_job(self, job):
        self.pending_jobs.append(job)
    
    def get_next_job(self, time):
        return [self.pending_jobs.pop(0)]

    def has_pending(self):
        return len(self.pending_jobs) > 0

    def get_route_length(self, jobs : list[Job]):
        tot_duration = 0
        tot_duration += jobs[0].get_duration()
        for i in range(1,len(jobs)-1):
            tot_duration +=  jobs[i].get_duration(jobs[i + 1].location)
        tot_duration += jobs[-1].get_duration()
        return tot_duration

class FCFS_Multi(Scheduler):
    
    def get_next_job(self, time):
        jobs = []
        while(self.pending_jobs and self.get_route_length(jobs + [self.pending_jobs[0]]) < self.DRONE_RANGE):
            jobs.append(self.pending_jobs.pop(0))
        return jobs

class LLV_Scheduler(Scheduler):

    def get_next_job(self, time):
        self.LLVJobSort(time)
        return [self.pending_jobs.pop(0)]

    def LLVJobSort(self, tc):
        for job in self.pending_jobs:
            job.NLV = job.PLV(self.pending_jobs, tc) - job.PGV(tc, self.pending_jobs)
        self.pending_jobs.sort(key = lambda x : x.NLV)

class SJF(Scheduler):
    def get_next_job(self, time):
        next_job = self.pending_jobs[0]
        for job in self.pending_jobs:
            if(job.get_duration() < next_job.get_duration()):
                next_job = job
        self.pending_jobs.remove(next_job)
        return [next_job]

class SJF_Multi(Scheduler):

    def add_job(self, job):
        self.pending_jobs.append(job)
        self.pending_jobs.sort(key = lambda x : x.get_duration())

    #def get_next_job(self, time):
    #    jobs = []
    #    while(self.pending_jobs and self.get_route_length(jobs + [self.pending_jobs[0]]) < self.DRONE_RANGE):
    #        jobs.append(self.pending_jobs.pop(0))
    #    print(len(jobs))
    #    return jobs
    
    def get_next_job(self, time):
        jobs = [self.pending_jobs.pop(0)]
        while(self.pending_jobs and self.get_route_length(jobs + [self.pending_jobs[0]]) < self.DRONE_RANGE and jobs[-1].get_duration() < jobs[-1].get_duration(self.pending_jobs[0].location)):
            jobs.append(self.pending_jobs.pop(0))
        return jobs