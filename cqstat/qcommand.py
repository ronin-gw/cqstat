import subprocess

from cluster import Cluster
from queue import Queue
from job import Job
from qstatxml import parse_job_list, parse_djob_info, parse_cluster_summary, parse_queue_info, parse_qhost

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


def get_cluster_info(options=None):
    command = "qstat -xml -g c " + (options if options else '')
    output = subprocess.check_output(command.split())

    return parse_cluster_summary(output)


def get_cluster(options):
    return [Cluster(**a) for a in get_cluster_info(options)]


def build_cluster(options, user_pattern, with_pjobs):
    clusters = {kwargs["name"]: Cluster(**kwargs) for kwargs in get_cluster_info(options)}

    command = "qstat -xml -f -u *" + options
    output = subprocess.check_output(command.split())

    qjinfo, pjinfo = parse_queue_info(output, with_pjobs)
    if with_pjobs:
        pending_jobs = [Job(**a) for a in pjinfo]
        for j in pending_jobs:
            if user_pattern.match(j.user.value):
                j.visible()
    else:
        pending_jobs = None

    for qinfo, rjinfo in qjinfo:
        queue = Queue(**qinfo)
        clusters[queue.resource].set_queue(queue)

        running_jobs = [Job(**a) for a in rjinfo]
        queue.append_jobs(running_jobs)
        for j in running_jobs:
            if user_pattern.match(j.user.value):
                j.visible()

    return clusters.values(), pending_jobs


def add_host_info(clusters):
    command = "qhost -xml"
    output = subprocess.check_output(command.split())

    hosts = parse_qhost(output)
    for cluster in clusters:
        for queue in cluster.queues:
            queue.set_host_info(**hosts[queue.hostname])
        cluster.set_host_info()
