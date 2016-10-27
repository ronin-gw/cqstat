import subprocess

from cluster import Cluster
from queue import Queue
from job import Job
from qstatxml import parse_job_list, parse_djob_info

TAG2KWARG = dict(
    JB_job_number="job_ID", JAT_prio="prior", JAT_ntix="ntckts", JB_nppri="nprior",
    JB_nurg="nurg", JB_urg="urg", JB_rrcontr="rrcontr", JB_wtcontr="wtcontr",
    JB_dlcontr="dlcontr", JB_priority="ppri", JB_name="name", JB_owner="user",
    JB_project="project", JB_department="department", state="state",
    JB_submission_time="sub_at", JAT_start_time="strt_at", JB_deadline="deadline",
    cpu_usage="cpu", mem_usage="mem", io_usage="io", tickets="tckts",
    JB_override_tickets="ovrts", JB_jobshare="jobshare", otickets="otckt",
    ftickets="ftckt", stickets="stckt", JAT_share="share", queue_name="queue",
    master="master_q", slots="slots", tasks="ja_task_id", jclass_name="jclass",
    hard_req_queue="h_resources", soft_req_queue="s_resources", master_hard_req_queue="master_h_res"
)
# predecessor_jobs_req, predecessor_jobs, requested_pe, granted_pe, JB_checkpoint_name. hard_request, def_hard_request, soft_request


def get_reduced_info(options):
    command = "qstat -xml" + options

    output = subprocess.check_output(command.split())

    running_jobs = [Job(**a) for a in parse_job_list(output, "queue_info/job_list")]
    pending_jobs = [Job(**a) for a in parse_job_list(output, "job_info/job_list")]

    return running_jobs, pending_jobs


def get_jvi_info(joblist):
    command = "qstat -xml -j "
    if joblist:
        command += joblist
    else:
        command += '*'

    output = subprocess.check_output(command.split())
    return parse_djob_info(output)


def add_jvi_info(jobs, joblist=None):
    if joblist is None:
        joblist = ','.join(j.id.value for j in jobs)
    attrs = get_jvi_info(joblist)

    for j in jobs:
        jid = j.id.value
        task_id = j.ja_task_id.value

        for k, v in attrs[jid].items():
            if k in Job.attributes:
                setattr(j, k, v)
            elif k == "tasks" and v:
                if task_id == "NA":
                    task_id = '1'
                elif task_id not in v:
                    continue
                for uaname, value in v[task_id].items():
                    setattr(j, uaname, value)
            elif k == "jh_resources":
                for rname, fvalue in v.items():
                    setattr(j, rname, fvalue)


def build_cluster(options, users):
    command = "qstat -g c" + options

    clusters = {}
    output = subprocess.check_output(command.split())

    for info in map(lambda l: l.split(), output.split('\n')[2:]):
        if not info:
            continue
        clusters[info[0]] = Cluster(*info)

    command = "qstat -f -u *" + options
    output = subprocess.check_output(command.split())

    for queue in _running_queue_generator(output, users):
        clusters[queue.resource].set_queue(queue)

    for c in clusters.values():
        c.apply_queue_stat()

    return clusters.values(), _get_pending_job(output, users)


def _running_queue_generator(qs_output, user_pattern):
    queue = None

    for info in map(lambda l: l.split(), qs_output.split('\n')[2:]):
        if not info:
            break

        elif not (len(info) == 1 and set(info[0]) == set(['-'])):
            if not info[0].isdigit():
                queue = Queue(*info)
            else:
                job = Job(*info)
                if user_pattern.match(job.user):
                    job.visible()
                queue.set_job(job)
        else:
            yield queue
            queue = None

    if queue:
        yield queue


def _get_pending_job(qs_output, user_pattern):
    pjline_no = -1
    for i, info in enumerate(map(lambda l: l.split(), qs_output.split('\n'))):
        if len(info) == 1 and set(info[0]) == set('#'):
            pjline_no = i
            break

    jobs = []
    if pjline_no >= 0:
        for line in qs_output.split('\n')[pjline_no + 3:]:
            if not line:
                break

            jobid, prior = line.split()[:2]
            name = line.lstrip()[len(jobid+prior)+2:][:10].rstrip()
            job = Job(*([jobid, prior, name] + line.lstrip()[len(jobid+prior)+13:].split()))

            if user_pattern.match(job.user):
                job.visible()
            jobs.append(job)

    return jobs


def add_host_info(queues):
    command = "qhost"

    hosts = {}
    output = subprocess.check_output(command.split())

    for info in map(lambda l: l.split(), output.split('\n')[2:]):
        if not info:
            continue
        hosts[info[0]] = info[2:]

    for queue in queues:
        queue.set_host_info(*hosts[queue.hostname])


def get_resource_option(jobids, rstr="s_vmem"):
    command = "qstat -j {}".format(','.join(jobids))
    output = subprocess.check_output(command.split())

    return {jobid: mem for jobid, mem in _resource_generator(output, rstr)}


def _resource_generator(output, rstr):
    rstr += '='
    jobid = mem = None
    for line in output.split('\n'):
        if line.startswith("job_number:"):
            jobid = line.split()[-1]

        elif line.startswith("hard resource_list:"):
            s_vmem = filter(lambda s: s.startswith(rstr), line.split()[-1].split(','))
            if s_vmem:
                mem = s_vmem[0].lstrip(rstr)

        elif (set(line) == set('=')) and jobid:
            yield jobid, mem
    else:
        yield jobid, mem
