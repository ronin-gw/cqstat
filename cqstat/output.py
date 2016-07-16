from cluster import Cluster


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

    print header
    print '-' * len(header)
    for c in clusters:
        c.print_status()


def print_status(clusters, pending_jobs, print_header=False):
    if any((clusters and any(c.has_visible_job() for c in clusters),
            pending_jobs and any(j.is_visible for j in pending_jobs),
            print_header)):
        print "job-ID   prior   name           user     state submit/start at     queue             slots ja-task-ID"
        print '-' * 100

    for cluster in clusters:
        for queue in cluster.queues:
            for job in queue.jobs:
                status = job.get_status()
                if not status:
                    continue

                print "{} {:.5f} {} {}  {}  {} {} {} {} {}".format(*(status[:7] + (queue.name,) + status[7:]))

    if pending_jobs:
        for job in pending_jobs:
            job.print_status()


def print_full_status(clusters, pending_jobs, sort, full):
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

            print "\t{}".format('-' * max(queue.get_infolen(), 85))
            for job in queue.jobs:
                job.print_status(indent=2)

    visible_job_num = sum(j.is_visible for j in pending_jobs) if pending_jobs else 0
    if visible_job_num:
        print '\n' + '#'*30 + "{} PENDING JOBS".format(visible_job_num).center(20) + '#'*30
        for job in pending_jobs:
            job.print_status()
