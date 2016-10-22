from __future__ import print_function
try:
    basestring
except NameError:
    basestring = str

import argparse
import os
import sys
import json
import getpass

from template import Coloring
from cluster import Cluster
from queue import Queue
from lib import generate_pattern, Re_dummy
from test import print_detail

CONFIG_PATH = "~/.cqstat_config.json"


class Invert(argparse.Action):
    def __init__(self, **kwargs):
        if "nargs" in kwargs:
            nargs = kwargs["nargs"]
            del kwargs["nargs"]
        else:
            nargs = 0
        super(Invert, self).__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if self.default not in (True, False):
            parser.error("Invalid argument default value {}; Invert action requires boolean as default of argument.".format(self.default))

        if values:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, not self.default)


class ParseJobState(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        statuses = set()
        hold_statuses = ['h'+s for s in "uosdja"]
        for status in hold_statuses + list("prsz"):
            if status in values:
                statuses.add(status)
                values = values.replace(status, '')

        if 'a' in values:
            statuses = statuses | set("psr")
            values = values.replace('a', '')
        if 'h' in values:
            statuses = statuses | set(hold_statuses)
            values = values.replace('h', '')

        if values:
            parser.error("Invalid job status in argument: {}".format(values))
        if not statuses:
            parser.error("-s requires at least one valid job status.")

        setattr(namespace, self.dest, list(statuses))


class ParseQueueState(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        queue_statuses = set("acdosuACDES")
        statuses = set(values)
        invalid_statuses = statuses - queue_statuses

        if invalid_statuses:
            parser.error("Invalid queue status in argument: {}".format(''.join(invalid_statuses)))

        setattr(namespace, self.dest, list(statuses))


class parse_eq(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        d = {}
        for v in values:
            for eq in v.split(','):
                splited = eq.split('=')
                if len(splited) == 1:
                    d[splited[0]] = ''
                else:
                    d[splited[0]] = splited[1]

        setattr(namespace, self.dest, d)


class split_comma(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            items = list(set(reduce(lambda a, b: a+b, map(lambda s: s.split(','), values), [])))
        else:
            items = []
        setattr(namespace, self.dest, items)


def parse_args():
    settings = _load_settings()

    parser = argparse.ArgumentParser(description="Colorful wrapper for Grid Engine qstat command", add_help=False)

    parser.add_argument("-h", action='help', default="==SUPPRESS==", help='Show this help message and exit.')
    parser.add_argument("--help", action="store_true", help='Show preview and current settings.')

    formats = parser.add_argument_group("formats", "Specify framework of format")
    formats.add_argument("-c", "--cluster-only",
                         action="store_true",
                         help="Show cluster information summary.")
    formats.add_argument("-f", "--full",
                         action=Invert, default=settings["full"],
                         help="Display information with queue statuses.")
    formats.add_argument("-F", "--full-with-resource",
                         nargs='*', action=split_comma, metavar="resource_name,...",
                         help="Full format with queue resource information.")
    formats.add_argument("-e", "--expand",
                         action=Invert, default=settings["expand"],
                         help="Full format display of information only visible jobs. (same as -ne)")
    formats.add_argument("-ext", "--extra",
                         action=Invert, default=settings["extra"],
                         help="Add ticket information.")
    formats.add_argument("-r", "--resource-req",
                         action=Invert, default=settings["resource"],
                         help="Add resource request information.")
    formats.add_argument("-urg", "--urgency",
                         action=Invert, default=settings["urgency"],
                         help="Add urgency information.")
    formats.add_argument("-pri", "--priority",
                         action=Invert, default=settings["priority"],
                         help="Add priority information.")
    formats.add_argument("-j", "--job",
                         nargs='+', action=split_comma, metavar="job_list",
                         help="Show scheduler job information")

    filters = parser.add_argument_group("filters", "Filtering options for jobs or queues")
    filters.add_argument("-l", "--resource",
                         nargs='+', action=parse_eq, metavar="resource{=value},...",
                         help="Filter queues by GE resources")
    filters.add_argument("-pe", "--paralell-env",
                         nargs='+', action=split_comma, metavar="pe_name",
                         help="Filter queues by GE paralell enviroments")
    filters.add_argument("-q", "--queue",
                         nargs='+', action=split_comma, metavar="wc_queue_list",
                         help="Define the GE queues")
    filters.add_argument("-u", "--user",
                         nargs='+', action=split_comma, default=[settings["username"]], metavar="user",
                         help="Display only jobs and queues being associated with the users")
    filters.add_argument("-a", "--all-user", action="store_true",
                         help="Display all user jobs (same as -u *)")
    filters.add_argument("-s", "--job-state",
                         action=ParseJobState, metavar="{a|c|d|o|s|u|A|C|D|E|S}",
                         help="Filter by job status")
    filters.add_argument("-qs", "--queue-state",
                         action=ParseQueueState, metavar="{p|r|s|z|hu|ho|hs|hd|hj|ha|h|a}[+]",
                         help="Filter by queue status")

    memory = parser.add_argument_group("memory", "Add memory informations")
    memory.add_argument("-m", "--required-memory",
                        nargs='?', choices=("s_vmem", "mem_req"),
                        action=Invert, default=settings["required-memory"],
                        help="Add required memory amount specified by GE resource option (take time to refer job status)")
    memory.add_argument("-ph", "--physical-memory",
                        action=Invert, default=settings["physical-memory"],
                        help="Add host memory usage")
    memory.add_argument("-sw", "--swapped-memory",
                        action=Invert, default=settings["swapped-memory"],
                        help="Add host swap usage")

    parser.add_argument("-p", "--pending-jobs",
                        action=Invert, default=settings["pending-jobs"],
                        help="Display pending jobs")

    others = parser.add_argument_group("others", "Some useful options")
    others.add_argument("-w", "--watch",
                        nargs='?', const=settings["watch"], default=False, metavar="sec",
                        help="Show status periodically (like watch command)")
    others.add_argument("--no-sort",
                        action=Invert, default=settings["no-sort"],
                        help="Disable sorting (As default, hosts are sorted by their status, usage and load average.)")
    others.add_argument("--split-ss-time",
                        action=Invert, default=settings["split-ss-time"],
                        help="Display submit and start time independently.")
    others.add_argument("--bleach",
                        action=Invert, default=settings["bleach"],
                        help="Disable coloring")

    additional = parser.add_argument_group("additiobals", "Add/Remove some attributes individually")
    additional.add_argument("--nurg", action=Invert, default=settings["nurg"])
    additional.add_argument("--nprior", action=Invert, default=settings["nprior"])
    additional.add_argument("--ntckts", action=Invert, default=settings["ntckts"])
    additional.add_argument("--urg", action=Invert, default=settings["urg"])
    additional.add_argument("--rrcontr", action=Invert, default=settings["rrcontr"])
    additional.add_argument("--wtcontr", action=Invert, default=settings["wtcontr"])
    additional.add_argument("--dicontr", action=Invert, default=settings["dicontr"])
    additional.add_argument("--ppri", action=Invert, default=settings["ppri"])
    additional.add_argument("--uid", action=Invert, default=settings["uid"])
    additional.add_argument("--group", action=Invert, default=settings["group"])
    additional.add_argument("--gid", action=Invert, default=settings["gid"])
    additional.add_argument("--supplementary-group", action=Invert, default=settings["supplementary-group"])
    additional.add_argument("--project", action=Invert, default=settings["project"])
    additional.add_argument("--department", action=Invert, default=settings["department"])
    additional.add_argument("--deadline", action=Invert, default=settings["deadline"])
    additional.add_argument("--wallclock", action=Invert, default=settings["wallclock"])
    additional.add_argument("--cpu", action=Invert, default=settings["cpu"])
    additional.add_argument("--mem", action=Invert, default=settings["mem"])
    additional.add_argument("--io", action=Invert, default=settings["io"])
    additional.add_argument("--iow", action=Invert, default=settings["iow"])
    additional.add_argument("--loops", action=Invert, default=settings["loops"])
    additional.add_argument("--vmem", action=Invert, default=settings["vmem"])
    additional.add_argument("--max-vmem", action=Invert, default=settings["max-vmem"])
    additional.add_argument("--tckts", action=Invert, default=settings["tckts"])
    additional.add_argument("--ovrts", action=Invert, default=settings["ovrts"])
    additional.add_argument("--otckt", action=Invert, default=settings["otckt"])
    additional.add_argument("--ftckt", action=Invert, default=settings["ftckt"])
    additional.add_argument("--stckt", action=Invert, default=settings["stckt"])
    additional.add_argument("--share", action=Invert, default=settings["share"])

    args = parser.parse_args()

    _setup_class(args, settings)

    # Build options for qstat call
    options = ''
    if args.resource:
        options += " -l " + ','.join(args.resource)
    if args.queue:
        options += " -q " + ','.join(args.queue)
    setattr(args, "options", options)

    # Define username search pattern
    if args.all_user:
        setattr(args, "user_pattern", Re_dummy(True))
    else:
        setattr(args, "user_pattern", generate_pattern(args.user))

    # TODO: Define job search pattern

    # Setting attributes from specified formats
    enable_attrs = set()
    if args.extra:
        enable_attrs |= set(("ntckts", "project", "department", "cpu", "mem", "io",
                             "tckts", "ovrts", "otckt", "ftckt", "stckt", "share"))
    if args.urgency:
        enable_attrs |= set(("nurg", "urg", "rrcontr", "wtcontr", "dicontr", "deadline"))
    if args.priority:
        enable_attrs |= set(("nurg", "nprior", "ntckts", "ppri"))
    for attr in enable_attrs:
        setattr(args, attr, getattr(args, attr) == settings[attr])

    # Return args of print help
    if args.help:
        print_detail(args, settings)
        sys.exit(0)
    else:
        return args


def _load_settings():
    COLORS = dict(
        black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37,
        b_black=90, b_red=91, b_green=92, b_yellow=93, b_blue=94, b_magenta=95, b_cyan=96, b_white=97,
    )

    default_settings = {
        "full": False,
        "expand": False,
        "extra": False,
        "resource": False,
        "urgency": False,
        "priority": False,
        "username": getpass.getuser(),
        "required-memory": False,
        "physical-memory": False,
        "swapped-memory": False,
        "pending-jobs": False,
        "watch": 5,
        "no-sort": False,
        "split-ss-time": False,
        "bleach": False,
        "nurg": False,
        "nprior": False,
        "ntckts": False,
        "urg": False,
        "rrcontr": False,
        "wtcontr": False,
        "dicontr": False,
        "ppri": False,
        "uid": False,
        "group": False,
        "gid": False,
        "supplementary-group": False,
        "project": False,
        "department": False,
        "deadline": False,
        "wallclock": False,
        "cpu": False,
        "mem": False,
        "io": False,
        "iow": False,
        "loops": False,
        "vmem": False,
        "max-vmem": False,
        "tckts": False,
        "ovrts": False,
        "otckt": False,
        "ftckt": False,
        "stckt": False,
        "share": False,
        "red": "red",
        "yellow": "yellow",
        "green": "green",
        "blue": "blue",
        "black": "b_black",
    }

    config_path = os.path.expanduser(CONFIG_PATH)

    user_settings = {}
    if os.path.exists(config_path):
        try:
            with open(config_path) as conf:
                user_settings = json.load(conf)
        except (IOError, ValueError) as e:
            print >>sys.stderr, "WARNING: Faild to open {} ({})".format(
                config_path,
                "{}: {}".format(e.__class__.__name__, str(e))
            )
    else:
        try:
            with open(config_path, "w") as conf:
                json.dump(default_settings, conf, sort_keys=True, indent=4)
        except (IOError, ValueError) as e:
            print >>sys.stderr, "WARNING: Faild to create {} ({})".format(
                config_path,
                "{}: {}".format(e.__class__.__name__, str(e))
            )

    for k, v in user_settings.copy().items():
        if k == "username":
            if not isinstance(v, basestring):
                del user_settings["username"]
            else:
                continue
        elif k not in COLORS and v not in (True, False):
            del user_settings[k]

    settings = dict(
        {k: v for k, v in user_settings.items() if k in default_settings},
        **{k: v for k, v in default_settings.items() if k not in user_settings}
    )

    for color in settings:
        if color in COLORS and settings[color] in COLORS:
            settings[color] = "\033[{}m".format(COLORS[settings[color]])

    return settings


def _setup_class(args, settings):
    Coloring.enable = not args.bleach
    Coloring.COLOR = {k: v for k, v in settings.items() if k in ("red", "yellow", "green", "blue", "black")}

    Cluster.args = args
    Queue.args = args


if __name__ == "__main__":
    print(parse_args())
