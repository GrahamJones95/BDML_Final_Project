import functools

class Scheduler:

    def __init__(self):
        self.pending_jobs = []

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
            job.NLV = job.PLV(self.pending_jobs, tc) - job.PGV(tc, self.pending_jobs)
        self.pending_jobs.sort(key = lambda x : x.NLV)

class SJF(Scheduler):
    def get_next_job(self, time):
        next_job = self.pending_jobs[0]
        for job in self.pending_jobs:
            if(job.duration_mean < next_job.duration_mean):
                next_job = job
        self.pending_jobs.remove(next_job)
        return next_job

class MOD(Scheduler):
    def get_next_job(self, time):
        self.LLVJobSort(time)
        return self.pending_jobs.pop(0)

    def LLVJobSort(self, tc):
        for job in self.pending_jobs:
            job.NLV = job.PGV(tc, self.pending_jobs)
        self.pending_jobs.sort(key = lambda x : x.NLV)

class MOD2(Scheduler):
    def get_next_job(self, time):
        self.LLVJobSort(time)
        return self.pending_jobs.pop(0)

    def LLVJobSort(self, tc):
        for job in self.pending_jobs:
            job.NLV = job.PLV(self.pending_jobs, tc)
        self.pending_jobs.sort(key = lambda x : x.NLV)
