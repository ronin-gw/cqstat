from __future__ import print_function

from job import Job


SEPARATOR = "  "


def _get_row_length(attr_lens):
    return sum(attr_lens) + (len(attr_lens) - 1) * len(SEPARATOR)


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


def _justify_string_with_multiheader(table, strip_len=None):
    headers = list(zip(*map(lambda a: a.name.split('\n'), table[0])))
    striptable = [map(lambda a: a.strfunc(0), v) for v in table]

    max_len = _get_width(headers + striptable, strip_len)
    headers = [[a.ljust(i) for a, i in zip(h, max_len)] for h in headers]
    table = [[a.strfunc(i) for a, i in zip(v, max_len)] for v in table]

    return headers, table, max_len


def _get_job_status(jobs, visible_only=True):
    return [status for status in map(lambda j: j.get_attributes(visible_only), jobs) if status]


def print_cluster_status(clusters):
    cluster_status = [status for status in map(lambda c: c.get_attributes(), clusters)]

    headers, cluster_status, attr_lens = _justify_string_with_multiheader(cluster_status)
    for h in headers:
        print(SEPARATOR.join(h))
    print('-' * _get_row_length(attr_lens))
    for c in cluster_status:
        print(SEPARATOR.join(c))


def print_job_status(jobs, visible_only=True):
    job_status = _get_job_status(jobs, visible_only)

    if job_status:
        header, job_status, attr_lens = _justify_string_with_header(job_status)
        print(SEPARATOR.join(header))
        print('-' * _get_row_length(attr_lens))
        for j in job_status:
            print(SEPARATOR.join(j))


def print_full_status(clusters, pending_jobs, sort, full):
    Job.attributes.remove("queue")

    for cluster in clusters:
        if full or cluster.has_visible_job():
            print(SEPARATOR.join(cluster.get_simple_status()))

        if sort:
            queues = sorted(cluster.queues, key=lambda q: q.key())
        else:
            queues = cluster.queues

        if not full:
            queues = filter(lambda q: q.has_visible_job(), queues)

        rut_len = map(max, zip(*(queue.get_rut_len() for queue in queues)))

        mem_len = {}
        for queue in queues:
            for k, v in queue.get_memory_len().items():
                mem_len[k] = max(mem_len.get(k, 0), v)

        swap_len = map(max, zip(*(queue.get_swap_len() for queue in queues)))

        status = []
        jobs = []
        for queue in queues:
            queue.set_rut(*rut_len)
            if mem_len:
                queue.set_memory_attrs(**mem_len)
            if swap_len:
                queue.set_swap_attrs(*swap_len)

            status.append(queue.get_attributes())
            jobs.append(queue.jobs)
        queue_status, q_attr_lens = _justify_string(status)

        for q_status, jobs in zip(queue_status, jobs):
            print((' ' * 8) + SEPARATOR.join(q_status))

            job_status, attr_lens = _justify_string(_get_job_status(jobs))

            if job_status:
                print((' ' * 8) + ('-' * (_get_row_length(attr_lens) + 8)))
            for j in job_status:
                print((' ' * 16) + SEPARATOR.join(j))

    visible_job_num = sum(j.is_visible for j in pending_jobs) if pending_jobs else 0
    if visible_job_num:
        job_status = _get_job_status(pending_jobs)

        header, job_status, attr_lens = _justify_string_with_header(job_status)
        row_length = _get_row_length(attr_lens)

        print('\n' + "   {} PENDING JOBS   ".format(visible_job_num).center(row_length, '#'))
        print('\n' + SEPARATOR.join(header))
        print('-' * row_length)
        for j in job_status:
            print(SEPARATOR.join(j))
