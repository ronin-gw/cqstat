from __future__ import print_function
import re

from cluster import Cluster
from job import Job


def _get_width(table, strip_len):
    len_table = [map(len, v) for v in table]
    if strip_len:
        len_table.append(strip_len)

    return list(map(max, zip(*len_table)))


def _justify_string(table, strip_len=None):
    striptable = [map(lambda a: a.strfunc(0), v) for v in table]

    max_len = _get_width(striptable, strip_len)
    table = [[a.strfunc(i) for a, i in zip(v, max_len)] for v in table]

    return table, max_len


def _justify_string_with_header(table, strip_len=None):
    header = list(map(lambda a: a.name, table[0]))
    striptable = [map(lambda a: a.strfunc(0), v) for v in table]

    max_len = _get_width([header] + striptable, strip_len)
    header = [a.ljust(i) for a, i in zip(header, max_len)]
    table = [[a.strfunc(i) for a, i in zip(v, max_len)] for v in table]

    return header, table, max_len


def _get_visible_job_status(jobs):
    return [status for status in map(lambda j: j.get_attributes(), jobs) if status]


def print_cluster_status(clusters):
    for attr in ("name", "used", "resv", "tot", "memtot", "rsvmem", "memuse", "swapus", "swapto"):
        setattr(Cluster, attr+"_len", max(len(str(getattr(c, attr, ''))) for c in clusters))

    name_len, slot_len, mem_len = clusters[0].get_infolen()

    memhed = (("mem/" if Cluster.physical_memory else '') +
              ("req/" if Cluster.required_memory else '') +
              ("tot mem" if Cluster.required_memory or Cluster.physical_memory else '') +
              ("  use/tot swap" if Cluster.swapped_memory else ''))

    header = "{}  {}  {}".format("queuename".ljust(name_len),
                                 "resv/used/tot (%)".center(slot_len),
                                 memhed.center(mem_len))

    print(header)
    print('-' * len(header))
    for c in clusters:
        c.print_status()


def print_status(clusters, pending_jobs):
    jobs = []

    for cluster in clusters:
        for queue in cluster.queues:
            for job in queue.jobs:
                job.queue = queue.name
                jobs.append(job)

    job_status = _get_visible_job_status(jobs + pending_jobs)

    if job_status:
        header, job_status, attr_lens = _justify_string_with_header(job_status)
        print(' '.join(header))
        print('-' * (sum(attr_lens) + len(header) - 1))
        for j in job_status:
            print(' '.join(j))


def print_full_status(clusters, pending_jobs, sort, full):
    Job.attributes.remove("queue")

    for cluster in clusters:
        if full or cluster.has_visible_job():
            cluster.print_simple_status()

        if sort:
            queues = sorted(cluster.queues, key=lambda q: q.key())
        else:
            queues = cluster.queues

        for queue in queues:
            if full or queue.has_visible_job():
                queue.print_status(indent=1)

            if not queue.has_visible_job():
                continue

            job_status, attr_lens = _justify_string(_get_visible_job_status(queue.jobs))

            if job_status:
                print((' ' * 8) + ('-' * (sum(attr_lens) + len(attr_lens) + 7)))
            for j in job_status:
                print((' ' * 16) + ' '.join(j))


    visible_job_num = sum(j.is_visible for j in pending_jobs) if pending_jobs else 0
    if visible_job_num:
        job_status = _get_visible_job_status(pending_jobs)

        header, job_status, attr_lens = _justify_string_with_header(job_status)
        row_length = sum(attr_lens) + len(attr_lens) - 1

        print('\n' + "   {} PENDING JOBS   ".format(visible_job_num).center(row_length, '#'))
        print('\n' + ' '.join(header))
        print('-' * row_length)
        for j in job_status:
            print(' '.join(j))
