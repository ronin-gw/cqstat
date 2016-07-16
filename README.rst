cqstat
======

A colorful command line tool substitutes for Grid Engine qstat command

.. image:: http://owncloud.a-fal.com/index.php/apps/files_sharing/ajax/publicpreview.php?x=2486&y=1806&a=true&file=cqstat.png&t=caPVu821M0bGOhq&scalingup=0


install
-------

From pip
  ``pip install cqstat``

or downlaod source from https://github.com/ronin-gw/cqstat

configure
---------

Edit ``~/cqstat_config.json`` to configure some defaults and colors. cqstat generates this file if not exists.

options
-------

* optional arguments

    ``-h``
        Show help message and exit.

    ``--help``
        Show preview and current settings.

        Filter and memory options affect the previews.

    ``-c/--cluster-only``
        Show cluster information summary.

    ``-p/--pending-jobs``
        Add pending jobs to output.

* format arguments

    ``-e/--expand``
        Full format display of queues which has visible job.

    ``-f/--full``
        Full format display of queues (even if queue doesn't have visible job).

* filter arguments

  ``-l`` and ``-q`` arguments will be passed to the GE ``qstat`` command.

    ``-l/--resource <resource>...``
        Filtering by the GE resources

    ``-q/--queue <queue>...``
        Filtering by the GE queue names.

    ``-u/--user <user>...``
        Display only jobs and queues being associated with the users.
        The login user name (``$USER`` environment valiable) will be used in omission.

    ``-a/--all-user``
        Display all jobs (same as -u \*)

* memory display options

  Outputs generate from these options depend on the GE ``qhost`` command.

    ``-r/--required-memory [{s_vmem,mem_req}]``
        Add required memory amount specified by GE resource option (``-l s_vmem`` or ``-l mem_req``).
        Using ``s_vmem`` value as default.
        As the case may be, this option takes additional time because of refering job status by ``qstat -j`` command.

    ``-m/--physical-memory``
        Add host machine memory usage.

    ``-s/--swapped-memory``
        Add host machine swap usage.

* others

    ``-w [sec], --watch [sec]``
        Show status periodically (like watch command)

    ``--no-sort``
        Disable queue sorting.

        As default, queue are sorted by their status, usage and load average.

    ``--bleach``
        Disable coloring (´・ω・｀)
