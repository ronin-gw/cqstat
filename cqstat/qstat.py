import sys
import time
import array
from termios import TIOCGWINSZ
import fcntl
import cStringIO
import contextlib

from setup import parse_args
from lib import flatten
from qcommand import build_cluster, add_host_info, get_resource_option
from output import print_cluster_status, print_full_status, print_status


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
    clusters, pending_jobs = build_cluster(args.options, args.user_pattern)
    pending_jobs = pending_jobs if args.pending_jobs else None

    if not (args.cluster_only or args.expand or args.full):
        print_status(clusters, pending_jobs, args.watch)

    elif args.required_memory:
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
