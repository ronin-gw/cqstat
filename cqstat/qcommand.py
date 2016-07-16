import subprocess

from cluster import Cluster
from queue import Queue
from job import Job


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
