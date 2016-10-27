from __future__ import print_function
import datetime

from template import Coloring
from lib import calc_suffix


class JobAttribute(Coloring):
    def rjust(self, l):
        return str(self.value).rjust(l)

    def center(self, l):
        return str(self.value).center(l)

    def ljust(self, l):
        return str(self.value).ljust(l)

    def float5(self, l):
        return '{:.5f}'.format(self.value).rjust(l)

    def float2(self, l):
        return '{:.2f}'.format(self.value).rjust(l)

    def int(self, l):
        return str(int(self.value)).rjust(l)

    def state(self, l):
        if l < 1:
            return self.value.center(l)

        if 'E' in self.value:
            coloring = self._color("red")
        elif 'w' in self.value or 's' in self.value or self.value == "Rq":
            coloring = self._color("yellow")
        elif 'r' in self.value:
            coloring = self._color("green")
        elif self.value == 't':
            coloring = self._color("blue")
        else:
            coloring = self._color()

        return coloring(self.value.center(l))

    def datetime(self, l):
        return self.value.strftime("%Y-%m-%d %H:%M:%S").ljust(l)

    def __init__(self, name, value, strfunc='l'):
        self.name = name

        if value is None:
            self.strfunc = lambda l: ' '*l
            self.value = "NA"
        elif strfunc == 'r':
            self.strfunc = self.rjust
            self.value = value
        elif strfunc == 'c':
            self.strfunc = self.center
            self.value = value
        elif strfunc == 'l':
            self.strfunc = self.ljust
            self.value = value
        elif strfunc == "sl":
            self.strfunc = self.ljust
            if Job.name_length < 1:
                self.value = str(value)
            else:
                self.value = str(value)[:Job.name_length]
        elif strfunc == "f5":
            self.strfunc = self.float5
            self.value = float(value)
        elif strfunc == "f2":
            self.strfunc = self.float2
            self.value = float(value)
        elif strfunc == 'i':
            self.strfunc = self.int
            self.value = int(value)
        elif strfunc == "state":
            self.strfunc = self.state
            self.value = value
        elif strfunc == 'd':
            self.strfunc = self.datetime
            self.value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            self.strfunc = strfunc
            self.value = value


class Job(object):
    name_length = 10
    attributes = ["id", "prior", "nurg", "nprior", "ntckts",
                  "urg", "rrcontr", "wtcontr", "dlcontr", "ppri",
                  "name", "user", "uid", "group", "gid", "sup_group",
                  "project", "department", "state",
                  "sub_strt_at", "sub_at", "strt_at", "deadline",
                  "wallclock", "cpu", "mem", "io", "iow", "loops", "vmem", "maxvmem",
                  "tckts", "ovrts", "otckt", "ftckt", "stckt", "share",
                  "queue", "jclass", "slots", "ja_task_id"]
    DEFAULT_FORMS = dict(
        id=("job-ID", 'r'),
        prior=("prior", "f5"),
        state=("state", "state"),
        jclass=("jclass", 'l'),
        nurg=("nurg", "f5"),
        nprior=("nprior", "f5"),
        ntckts=("ntckts", "f5"),
        group=("group", 'l'),
        sup_group=("sup_group", 'l'),
        project=("project", 'l'),
        department=("department", 'l'),
        sub_at=("submit at", 'd'),
        strt_at=("start at", 'd'),
        sub_strt_at=("submit/start at", 'd'),
        deadline=("deadline", 'd'),
        share=("share", "f2"),
        jobshare=("jobshare", 'i'),
        slots=("slots", 'r')
    )

    def __setattr__(self, name, value):
        if name in Job.attributes and not isinstance(value, JobAttribute):
            label, strfunc = Job.DEFAULT_FORMS.get(name, (name, 'l'))
            self.__dict__[name] = JobAttribute(label, value, strfunc)
        else:
            self.__dict__[name] = value

    def __init__(
        self, job_ID, prior, name, user, state, jclass=None,
        nurg=None, nprior=None, ntckts=None,
        urg=None, rrcontr=None, wtcontr=None, dlcontr=None, ppri=None,
        uid=None, group=None, gid=None, sup_group=None,
        project=None, department=None,
        sub_strt_at=None, sub_at=None, strt_at=None, deadline=None,
        wallclock=None, cpu=None, mem=None, io=None,
        iow=None, loops=None, vmem=None, maxvmem=None,
        tckts=None, ovrts=None, otckt=None, ftckt=None, stckt=None,
        share=None, jobshare=None, queue=None, slots=None, ja_task_id=None,
        master_q=None, h_resources=None, master_h_res=None, s_resources=None, binding=None,
        sge_o_home=None, sge_o_log_name=None, sge_o_path=None,
        sge_o_shell=None, sge_o_workdir=None, sge_o_host=None,
        account=None, stdout_path_list=None, stderr_path_list=None,
        mail_list=None, notify=None, restart=None, env_list=None, mbind=None,
        submit_cmd=None, exec_host_list=None, granted_req=None, scheduling=None
    ):
        # assign attributes
        self.id = job_ID
        self.prior = prior
        self.name = name
        self.user = user
        self.state = state
        self.jclass = jclass
        self.nurg = nurg
        self.nprior = nprior
        self.ntckts = ntckts
        self.urg = urg
        self.rrcontr = rrcontr
        self.wtcontr = wtcontr
        self.dlcontr = dlcontr
        self.ppri = ppri
        self.uid = uid
        self.group = group
        self.gid = gid
        self.sup_group = sup_group
        self.project = project
        self.department = department
        self.sub_at = sub_at
        self.strt_at = strt_at
        if sub_strt_at:
            self.sub_strt_at = sub_strt_at
        elif strt_at:
            self.sub_strt_at = strt_at
        elif sub_at:
            self.sub_strt_at = sub_at
        self.deadline = deadline
        self.wallclock = wallclock
        self.cpu = cpu
        self.mem = mem
        self.io = io
        self.iow = iow
        self.loops = loops
        self.vmem = vmem
        self.maxvmem = maxvmem
        self.tckts = tckts
        self.ovrts = ovrts
        self.otckt = otckt
        self.ftckt = ftckt
        self.stckt = stckt
        self.share = share
        self.jobshare = jobshare
        self.queue = queue
        self.slots = slots
        self.ja_task_id = ja_task_id
        self.master_q = master_q
        self.h_resources = h_resources
        self.master_h_res = master_h_res
        self.s_resources = s_resources
        self.binding = binding
        self.sge_o_home = sge_o_home
        self.sge_o_log_name = sge_o_log_name
        self.sge_o_path = sge_o_path
        self.sge_o_shell = sge_o_shell
        self.sge_o_workdir = sge_o_workdir
        self.sge_o_host = sge_o_host
        self.account = account
        self.stdout_path_list = stdout_path_list
        self.stderr_path_list = stderr_path_list
        self.mail_list = mail_list
        self.notify = notify
        self.restart = restart
        self.env_list = env_list
        self.mbind = mbind
        self.submit_cmd = submit_cmd
        self.exec_host_list = exec_host_list
        self.granted_req = granted_req
        self.scheduling = scheduling

        # define status
        self.is_visible = False

    def visible(self):
        self.is_visible = True

    def set_vmem(self, vmem):
        self.reserved_memory = calc_suffix(vmem[self.id.value]) * int(self.slots.value)

    def get_attributes(self, visible_only=True):
        if not self.is_visible and visible_only:
            return None

        return tuple([getattr(self, n) for n in Job.attributes])
