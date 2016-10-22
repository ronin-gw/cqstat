from __future__ import print_function
from template import Coloring
from lib import calc_suffix


class Job(Coloring):
    attributes = ["job-ID", "prior", "nurg", "nprior", "ntckts",
                  "urg", "rrcontr", "wtcontr", "dicontr", "ppri",
                  "name", "user", "uid", "group", "gid", "sup_group",
                  "project", "department", "state",
                  "sub_strt_at", "sub_at", "strt_at", "deadline",
                  "wallclock", "cpu", "mem", "io", "iow", "loops", "vmem", "max_vmem",
                  "tckts", "ovrts", "otckt", "ftckt", "stckt", "share",
                  "queue", "jclass", "slots", "ja_task_id"]

    def __init__(
        self, job_ID, prior, name, user, state, jclass,
        nurg=None, nprior=None, ntckts=None,
        urg=None, rrcontr=None, wtcontr=None, dicontr=None, ppri=None,
        uid=None, group=None, gid=None, sup_group=None,
        project=None, department=None,
        sub_strt_at=None, sub_at=None, strt_at=None, deadline=None,
        wallclock=None, cpu=None, mem=None, io=None,
        iow=None, loops=None, vmem=None, max_vmem=None,
        tckts=None, ovrts=None, otckt=None, ftckt=None, stckt=None,
        share=None, queue=None, slots=None, ja_task_id=None,
        master_q=None, h_resources=None, master_h_res=None, s_resources=None, binding=None,
        sge_o_home=None, sge_o_log_name=None, sge_o_path=None,
        sge_o_shell=None, sge_o_workdir=None, sge_o_host=None,
        account=None, stdout_path_list=None, stderr_path_list=None,
        mail_list=None, notify=None, restart=None, env_list=None, mbind=None,
        submit_cmd=None, exec_host_list=None, granted_req=None, scheduling=None
    ):
        # assign attributes
        self.id = job_ID
        self.prior = float(prior)
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
        self.dicontr = dicontr
        self.ppri = ppri
        self.uid = uid
        self.group = group
        self.gid = gid
        self.sup_group = sup_group
        self.project = project
        self.department = department
        self.sub_strt_at = sub_strt_at
        self.sub_at = sub_at
        self.strt_at = strt_at
        self.deadline = deadline
        self.wallclock = wallclock
        self.cpu = cpu
        self.mem = mem
        self.io = io
        self.iow = iow
        self.loops = loops
        self.vmem = vmem
        self.max_vmem = max_vmem
        self.tckts = tckts
        self.ovrts = ovrts
        self.otckt = otckt
        self.ftckt = ftckt
        self.stckt = stckt
        self.share = share
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

        # colorize state
        self._state = self.state
        if 'E' in self.state:
            coloring = self._color("red")
        elif 'w' in self.state or self.state == "Rq":
            coloring = self._color("yellow")
        elif 'r' in self.state:
            coloring = self._color("green")
        elif self.state == 't':
            coloring = self._color("blue")
        else:
            coloring = self._color()
        self.col_state = coloring(self.state)

    def visible(self):
        self.is_visible = True

    def set_vmem(self, vmem):
        self.reserved_memory = calc_suffix(vmem[self.id]) * int(self.slots)

    def get_status(self):
        if not self.is_visible:
            return None

        self.state = self.col_state
        status = tuple([self.id] + [getattr(self, n) for n in Job.attributes[1:]])
        self.state = self._state

        return status
