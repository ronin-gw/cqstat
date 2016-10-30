from __future__ import print_function
from cluster import Cluster
from queue import Queue
from job import Job
from output import print_full_status, print_cluster_status


def print_detail(args, settings):
    j = Job("12345", "0.0", "job12345", settings["username"], 'r', '',
            0., 0., 0., 0, 0, 0, 0, 0,
            100, "tgroup", 100, "tgroup",
            "test project", "test department",
            "2016-01-01T12:34:56.000", "2016-01-01T12:33:21.000", "2016-01-01T12:34:56.000", None,
            "00:01:35", "00:01:00", "12.00000 GBs", "0.00984 GB",
            "0.489 s", "1563", "12.000G", "12.000G",
            0, 0, 0, 0, 0,
            0., None, "6", "1")
    jo = Job("12344", "0.0", "job12344", "user01", 'r', '',
             0., 0., 0., 0, 0, 0, 0, 0,
             101, "tgroup", 100, "tgroup",
             "test project", "test department",
             "2016-01-01T12:34:00.000", "2016-01-01T12:33:00.000", "2016-01-01T12:34:00.000", None,
             "00:01:00", "00:00:35", "8.00000 GBs", "0.00263 GB",
             "0.135 s", "8275", "8.000G", "8.000G",
             0, 0, 0, 0, 0,
             0., None, "4", "1")
    jp = Job("12346", "0.0", "job12346", "user02", 'qw', '',
             0., 0., 0., 0, 0, 0, 0, 0,
             102, "tgroup", 100, "tgroup",
             "test project", "test department",
             "2016-01-01T12:35:28.000", "2016-01-01T12:35:28.000", None, None,
             None, None, None, None,
             None, None, None, None,
             0, 0, 0, 0, 0,
             0., None, "10", "1")
    ja = Job("12340", "0.0", "job12340", "user03", 'r', '',
             0., 0., 0., 0, 0, 0, 0, 0,
             101, "tgroup", 100, "tgroup",
             "test project", "test department",
             "2016-01-01T12:30:11.000", "2016-01-01T12:30:00.000", "2016-01-01T12:30:11.000", None,
             "00:00:11", "00:00:10", "134.00000 GBs", "0.03246 GB",
             "0.354 s", "2345", "57.400G", "57.400G",
             0, 0, 0, 0, 0,
             0., None, "20", "1")

    q = Queue("cluster01.q@host001", "BIP", "6/10/20", "4.71", "lx-amd64")
    qo = Queue("cluster01.q@host002", "BIP", "0/0/20", "0.03", "lx-amd64")
    q1 = Queue("cluster02.q@host003", "BIP", "0/20/20", "21.38", "lx-amd64", "a")
    q2 = Queue("cluster02.q@host004", "BIP", "0/0/20", "0.13", "lx-amd64", "d")

    c = Cluster("cluster01.q", "4.38", "10", "0", "40", "40", "0", "0")
    c2 = Cluster("cluster02.q", "4.38", "10", "0", "40", "40", "0", "0")

    q.set_job(j)
    q.set_job(jo)
    q1.set_job(ja)
    c.set_queue(q)
    c.set_queue(qo)
    c2.set_queue(q1)
    c2.set_queue(q2)

    for job in (j, jo, jp, ja):
        if args.user_pattern.match(job.user.value):
            job.visible()

    q.set_host_info("20", "2", "10", "20", "4.71", "64G", "21.2G", "7.9G", "108M")
    q1.set_host_info("20", "2", "10", "20", "21.38", "64G", "57.4G", "11.3G", "3.1G")
    q2.set_host_info("20", "2", "10", "20", "0.13", "64G", "461.4M", "3.1G", "51M")
    qo.set_host_info("20", "2", "10", "20", "0.03", "64G", "203.9M", "4.1G", "71M")

    c.set_host_info()
    c2.set_host_info()

    c.set_vmem({"12344": "3G", "12345": "4G"})
    c2.set_vmem({"12340": "3G"})

    c.set_queue_printlen()
    c2.set_queue_printlen()

    pj = [jp] if args.pending_jobs else []

    print("preview:")
    print()
    # print_status([c, c2], pj)
    print()
    print()
    print("full format preview (-e/-f):")
    print()
    print("<cluster> used/total slot (rate)")
    print(
        "\t<queuename> qtype resv/used/tot load_avg " +
        (
            ("use/" if args.physical_memory else '') +
            ("req/" if args.required_memory else '') +
            ("tot mem" if args.required_memory or args.physical_memory else '') +
            ("  use/tot swap" if args.swapped_memory else '') +
            "  arch states"
        )
    )
    print()
    print_full_status([c, c2], pj, not args.no_sort, True)
    print()
    print()
    print("cluster status preview (-c):")
    print()
    print_cluster_status([c, c2])
    print()
    print()

    print("current default settings (edit ~/.cqstat_config.json to change these defaults):")
    l = max(map(len, settings))
    for k, v in sorted(settings.items()):
        print("  {}\t{}".format(k.ljust(l+4), repr(v)))
