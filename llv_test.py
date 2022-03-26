from scheduler import LLV_Scheduler
from job import Job, ValueFunction, DistType
from scipy.stats import lognorm, norm

value_funcs = [ValueFunction("(0, 100), (360, 90), (720, 80), (1080, 70), (1440, 60), (1800, 50), (2160, 40), (2520, 30), (2880, 20), (3240, 10), (3600, -5)"),\
            ValueFunction("(0, 100), (50, 50), (100, 0)")]

job = Job(1, 100, DistType.Normal, 50, 10, value_funcs[1], -1, -1, norm(50))

#print(f"Job ED = {job.ED()} EV @ 100 = {job.EV(100)} EV @ 200 = {job.EV(200)} EV @ 3705 = {job.EV(3705)}")

job1 = Job(1, 100, DistType.Normal, 50, 10, value_funcs[1], -1, -1, norm(50))
job2 = Job(1, 100, DistType.Normal, 50, 10, value_funcs[1], -1, -1, norm(50))

jobs = [job1, job2]

print(job1.PLV(jobs,150))
print(job1.ED_avg(jobs))