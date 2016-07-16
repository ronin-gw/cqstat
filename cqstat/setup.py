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


def parse_args():
    settings = _load_settings()

    parser = argparse.ArgumentParser(description="Colorful wrapper for Grid Engine qstat command", add_help=False)

    parser.add_argument("-h", action='help', default="==SUPPRESS==", help='Show this help message and exit')
    parser.add_argument("--help", action="store_true", help='Show preview and current settings')

    parser.add_argument("-c", "--cluster-only",
                        action="store_true",
                        help="Show cluster information summary")

    formats = parser.add_argument_group("formats")
    formats.add_argument("-e", "--expand",
                         action=Invert, default=settings["expand"],
                         help="Full format display of information only visible jobs")
    formats.add_argument("-f", "--full",
                         action=Invert, default=settings["full"],
                         help="Full format display of information")

    filters = parser.add_argument_group("filters")
    filters.add_argument("-l", "--resource", nargs='+',
                         help="Define the GE resources")
    filters.add_argument("-q", "--queue", nargs='+',
                         help="Define the GE queues")
    filters.add_argument("-u", "--user", nargs='+', default=[settings["username"]],
                         help="Display only jobs and queues being associated with the users")
    filters.add_argument("-a", "--all-user", action="store_true",
                         help="Display all user jobs (same as -u *)")

    memory = parser.add_argument_group("memory")
    memory.add_argument("-r", "--required-memory",
                        nargs='?', choices=("s_vmem", "mem_req"),
                        action=Invert, default=settings["required-memory"],
                        help="Add required memory amount specified by GE resource option (take time to refer job status)")
    memory.add_argument("-m", "--physical-memory",
                        action=Invert, default=settings["physical-memory"],
                        help="Add host memory usage")
    memory.add_argument("-s", "--swapped-memory",
                        action=Invert, default=settings["swapped-memory"],
                        help="Add host swap usage")

    parser.add_argument("-p", "--pending-jobs",
                        action=Invert, default=settings["pending-jobs"],
                        help="Display pending jobs")

    others = parser.add_argument_group("others")
    others.add_argument("-w", "--watch",
                        nargs='?', const=settings["watch"], default=False, metavar="sec",
                        help="Show status periodically (like watch command)")

    others.add_argument("--no-sort",
                        action=Invert, default=settings["no-sort"],
                        help="Disable sorting (As default, hosts are sorted by their status, usage and load average.)")
    others.add_argument("--bleach",
                        action=Invert, default=settings["bleach"],
                        help="Disable coloring")

    args = parser.parse_args()

    _setup_class(args, settings)

    options = ''
    if args.resource:
        options += " -l " + ','.join(args.resource)
    if args.queue:
        options += " -q " + ','.join(args.queue)
    setattr(args, "options", options)

    if args.all_user:
        setattr(args, "user_pattern", Re_dummy(True))
    else:
        setattr(args, "user_pattern", generate_pattern(args.user))

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
        "expand": False,
        "full": False,
        "required-memory": False,
        "physical-memory": False,
        "swapped-memory": False,
        "pending-jobs": False,
        "no-sort": False,
        "bleach": False,
        "username": getpass.getuser(),
        "red": "red",
        "yellow": "yellow",
        "green": "green",
        "blue": "blue",
        "black": "b_black",
        "watch": 5
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

    for k, v in user_settings.items():
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

    Cluster.required_memory = True if args.required_memory else False
    Cluster.physical_memory = args.physical_memory
    Cluster.swapped_memory = args.swapped_memory

    Queue.required_memory = True if args.required_memory else False
    Queue.physical_memory = args.physical_memory
    Queue.swapped_memory = args.swapped_memory
