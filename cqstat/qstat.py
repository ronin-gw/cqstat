import sys
import time
import array
from termios import TIOCGWINSZ
import fcntl
import contextlib

from startup import parse_args
from qcommand import get_reduced_info, add_jvi_info, get_cluster, build_cluster, add_host_info
from output import print_job_status, print_cluster_status, print_full_status

if sys.version_info > (3, ):
    from functools import reduce
    from io import StringIO
else:
    from cStringIO import StringIO


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
    with contextlib.closing(StringIO()) as strio:
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
    if args.job:
        pass

    elif not args.full_format:
        running_jobs, pending_jobs = get_reduced_info(args.options)
        if args.need_jvi:
            add_jvi_info(running_jobs + pending_jobs, '*' if "-u *" in args.options else None)
        print_job_status(running_jobs + pending_jobs, visible_only=False)

    elif args.cluster_only and not args.required_memory:
        clusters = get_cluster(args.options + (" -ext" if args.extra else ''))
        if args.physical_memory or args.swapped_memory:
            add_host_info(clusters)

        print_cluster_status(clusters)

    else:
        clusters, pending_jobs = build_cluster(args.options, args.user_pattern, args.pending_jobs)
        running_jobs = reduce(lambda a, b: a + b, map(lambda c: c.get_running_jobs(), clusters))

        if args.need_jvi:
            add_jvi_info(running_jobs + pending_jobs, '*')

        if args.required_memory or args.physical_memory or args.swapped_memory:
            add_host_info(clusters)
            for cluster in clusters:
                if args.required_memory:
                    cluster.summation_reqmem("s_vmem" if args.required_memory is True else args.required_memory)

        if args.cluster_only:
            print_cluster_status(clusters)
        else:
            print_full_status(clusters, pending_jobs, not args.no_sort, args.full)


if __name__ == "__main__":
    main()
