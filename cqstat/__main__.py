import os
import sys

import qstat
from lib import flatten

# ignore broken pipe error
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)


def main():
    # CHECK ENVIRON #
    listpath = flatten(os.listdir(path) for path in os.environ["PATH"].split(':') if os.path.exists(path))
    if not (("qstat" in listpath) and ("qhost" in listpath)):
        sys.exit("Error: qstat or qhost command not found in your path.")

    try:
        qstat.main()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
