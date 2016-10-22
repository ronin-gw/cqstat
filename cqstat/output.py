from __future__ import print_function
import re

from cluster import Cluster
from job import Job


def _catch_ansi_code(group):
    def _f(text):
        m = re.match("^(\\x1b\[\d+m)?(.+?)(\\x1b\[0m)?$", text)
        return (m.group(group) or '') if m else ''
    return _f


def _decomp_attrs(table, strip_len):
    ansi_stock = [map(_catch_ansi_code(1), v) for v in table]
    table = [map(_catch_ansi_code(2), v) for v in table]
    len_table = [map(len, v) for v in table]
    if strip_len:
        len_table.append(strip_len)

    max_len = map(max, zip(*len_table))
    return table, ansi_stock, max_len


def _justify_string(table, strip_len=None):
    table, ansi_stock, max_len = _decomp_attrs(table, strip_len)
    table = [[a.rjust(i) for a, i in zip(v, max_len)] for v in table]
    table = [
        [a + r + "\x1b[0m" if a else r for r, a in zip(row, ansi)]
        for row, ansi in zip(table, ansi_stock)
    ]
    return table, max_len


def _justify_string_with_header(header, table, strip_len=None):
    table, ansi_stock, max_len = _decomp_attrs([header] + table, strip_len)
    table = (
        [[a.ljust(i) for a, i in zip(table[0], max_len)]] +
        [[a.rjust(i) for a, i in zip(v, max_len)] for v in table[1:]]
    )
    table = [
        [a + r + "\x1b[0m" if a else r for r, a in zip(row, ansi)]
        for row, ansi in zip(table, ansi_stock)
    ]
    return table[0], table[1:], max_len


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
    header = Job.attributes
    jobs = []

    for cluster in clusters:
        for queue in cluster.queues:
            for job in queue.jobs:
                job.queue = queue.name
                jobs.append(job)

    jobs = jobs + pending_jobs
    job_status = [
        map(lambda x: 'NA' if x is None else str(x), status)
        for status in map(lambda j: j.get_status(), jobs) if status
    ]

    if job_status:
        header, job_status, attr_lens = _justify_string_with_header(header, job_status)
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

            job_status = [
                map(lambda x: 'NA' if x is None else str(x), status)
                for status in map(lambda j: j.get_status(), queue.jobs) if status
            ]

            job_status, attr_lens = _justify_string(job_status)

            if job_status:
                print((' ' * 8) + ('-' * (sum(attr_lens) + len(attr_lens) + 7)))
            for j in job_status:
                print((' ' * 16) + ' '.join(j))


    visible_job_num = sum(j.is_visible for j in pending_jobs) if pending_jobs else 0
    if visible_job_num:
        job_status = [
            map(lambda x: 'NA' if x is None else str(x), status)
            for status in map(lambda j: j.get_status(), pending_jobs) if status
        ]

        header, job_status, attr_lens = _justify_string_with_header(Job.attributes, job_status)
        row_length = sum(attr_lens) + len(attr_lens) - 1

        print('\n' + "   {} PENDING JOBS   ".format(visible_job_num).center(row_length, '#'))
        print('\n' + ' '.join(header))
        print('-' * row_length)
        for j in job_status:
            print(' '.join(j))
