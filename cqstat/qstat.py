import sys
import time
import array
from termios import TIOCGWINSZ
import fcntl
import contextlib
try:
    import cStringIO
except ImportError:
    from io import StringIO as cStringIO

from startup import parse_args
from lib import flatten
from qcommand import get_reduced_info, add_jvi_info, build_cluster, add_host_info, get_resource_option
from output import print_job_status, print_cluster_status, print_full_status, print_status


def main():
    args = parse_args()

    if args.watch:
        watch_qstat(args)
    else:
        qstat(args)


def watch_qstat(args):
    # get terminal size
    buf = array.array('H', ([0] * 4))
    stdfileno = sys.stdout.fileno()
    fcntl.ioctl(stdfileno, TIOCGWINSZ, buf, 1)
    height, width = buf[:2]

    interval = round(float(args.watch), 1)

    header = "Every {}s : ".format(interval)
    cmdline = ' '.join(sys.argv)

    if len(header)+19+len(cmdline) > width:
        header += ' '*(width - len(header) - 19)
    else:
        header += cmdline + ' '*(width - len(header) - 19 - len(cmdline))

    # prevent display flickering due to qstat() time lag
    with contextlib.closing(cStringIO.StringIO()) as strio:
        sys.stdout = strio

        while True:
            sys.stdout.write("\033[H\033[J{}\n\n".format(header + time.strftime("%Y-%m-%d %H:%M:%S")))
            qstat(args)
            sys.stdout.seek(0)
            sys.__stdout__.writelines(l for i, l in enumerate(sys.stdout) if i < height-1)

            sys.stdout.seek(0)
            sys.stdout.truncate()

            time.sleep(interval)


def qstat(args):
    if not any((args.cluster_only, args.full, args.full_with_resource, args.expand, args.resource_req, args.job)):
        running_jobs, pending_jobs = get_reduced_info(args.options)
        if args.need_jvi:
            add_jvi_info(running_jobs + pending_jobs, '*' if "-u *" in args.options else None)
        print_job_status(running_jobs + pending_jobs, visible_only=False)

    # clusters, pending_jobs = build_cluster(args.options, args.user_pattern)
    # pending_jobs = pending_jobs if args.pending_jobs else None
    #
    # if not (args.cluster_only or args.expand or args.full):
    #     print_status(clusters, pending_jobs)

    elif args.required_memory:
        clusters, pending_jobs = build_cluster(args.options, args.user_pattern)
        pending_jobs = pending_jobs if args.pending_jobs else None

        jobids = flatten(c.get_jobids() for c in clusters)
        if isinstance(args.required_memory, str):
            vmem_list = get_resource_option(jobids, args.required_memory)
        else:
            vmem_list = get_resource_option(jobids)

        for cluster in clusters:
            add_host_info(cluster.queues)
            cluster.set_host_info()
            cluster.set_vmem(vmem_list)
            cluster.set_queue_printlen()

    elif args.physical_memory or args.swapped_memory:
        for cluster in clusters:
            add_host_info(cluster.queues)
            cluster.set_host_info()
            cluster.set_queue_printlen()

    if args.cluster_only:
        print_cluster_status(clusters)
    elif args.expand or args.full:
        print_full_status(clusters, pending_jobs, not args.no_sort, args.full)


if __name__ == "__main__":
    main()
