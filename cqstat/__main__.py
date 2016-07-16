import os
import sys

import qstat
from lib import flatten


def main():
    # CHECK ENVIRON #
    listpath = flatten(os.listdir(path) for path in os.environ["PATH"].split(':') if os.path.exists(path))
    if not (("qstat" in listpath) and ("qhost" in listpath)):
        sys.exit("Error: qstat or qhost command not found in your path.")

    try:
        qstat.main()
    except IOError as (errno, strerror):
        if errno == 32:  # Broken pipe
            pass
        else:
            raise IOError(errno, strerror)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
