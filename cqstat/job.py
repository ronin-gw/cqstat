from __future__ import print_function
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
        elif 'w' in self.value or self.value == "Rq":
            coloring = self._color("yellow")
        elif 'r' in self.value:
            coloring = self._color("green")
        elif self.value == 't':
            coloring = self._color("blue")
        else:
            coloring = self._color()

        return coloring(self.value.center(l))

    def __init__(self, name, value, strfunc='r'):
        self.name = name

        if strfunc == 'r':
            self.strfunc = self.rjust
            self.value = value
        elif strfunc == 'c':
            self.strfunc = self.center
            self.value = value
        elif strfunc == 'l':
            self.strfunc = self.ljust
            self.value = value
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
        else:
            self.strfunc = strfunc
            self.value = value


class Job(object):
    attributes = ["id", "prior", "nurg", "nprior", "ntckts",
                  "urg", "rrcontr", "wtcontr", "dicontr", "ppri",
                  "name", "user", "uid", "group", "gid", "sup_group",
                  "project", "department", "state",
                  "sub_strt_at", "sub_at", "strt_at", "deadline",
                  "wallclock", "cpu", "mem", "io", "iow", "loops", "vmem", "max_vmem",
                  "tckts", "ovrts", "otckt", "ftckt", "stckt", "share",
                  "queue", "jclass", "slots", "ja_task_id"]

    def __setattr__(self, name, value):
        if name in Job.attributes and not isinstance(value, JobAttribute):
            self.__dict__[name] = JobAttribute(name, value)
        else:
            self.__dict__[name] = value

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
        attr = JobAttribute
        self.id = attr("job-ID", job_ID)
        self.prior = attr("prior", prior, "f5")
        self.name = attr("name", name, 'l')
        self.user = attr("user", user, 'l')
        self.state = attr("state", state, "state")
        self.jclass = attr("jclass", jclass, 'l')
        self.nurg = attr("nurg", nurg, "f5")
        self.nprior = attr("nprior", nprior, "f5")
        self.ntckts = attr("ntckts", ntckts, "f5")
        self.urg = attr("urg", urg)
        self.rrcontr = attr("rrcontr", rrcontr)
        self.wtcontr = attr("wtcontr", wtcontr)
        self.dicontr = attr("dicontr", dicontr)
        self.ppri = attr("ppri", ppri)
        self.uid = attr("uid", uid)
        self.group = attr("group", group, 'l')
        self.gid = attr("gid", gid)
        self.sup_group = attr("sup_group", sup_group, 'l')
        self.project = attr("project", project, 'l')
        self.department = attr("department", department, 'l')
        self.sub_strt_at = attr("sub_strt_at", sub_strt_at)
        self.sub_at = attr("sub_at", sub_at)
        self.strt_at = attr("strt_at", strt_at)
        self.deadline = attr("deadline", deadline)
        self.wallclock = attr("wallclock", wallclock)
        self.cpu = attr("cpu", cpu)
        self.mem = attr("mem", mem)
        self.io = attr("io", io)
        self.iow = attr("iow", iow)
        self.loops = attr("loops", loops)
        self.vmem = attr("vmem", vmem)
        self.max_vmem = attr("max_vmem", max_vmem)
        self.tckts = attr("tckts", tckts)
        self.ovrts = attr("ovrts", ovrts)
        self.otckt = attr("otckt", otckt)
        self.ftckt = attr("ftckt", ftckt)
        self.stckt = attr("stckt", stckt)
        self.share = attr("share", share, "f2")
        self.queue = attr("queue", queue)
        self.slots = attr("slots", slots)
        self.ja_task_id = attr("ja_task_id", ja_task_id)
        self.master_q = attr("master_q", master_q)
        self.h_resources = attr("h_resources", h_resources)
        self.master_h_res = attr("master_h_res", master_h_res)
        self.s_resources = attr("s_resources", s_resources)
        self.binding = attr("binding", binding)
        self.sge_o_home = attr("sge_o_home", sge_o_home)
        self.sge_o_log_name = attr("sge_o_log_name", sge_o_log_name)
        self.sge_o_path = attr("sge_o_path", sge_o_path)
        self.sge_o_shell = attr("sge_o_shell", sge_o_shell)
        self.sge_o_workdir = attr("sge_o_workdir", sge_o_workdir)
        self.sge_o_host = attr("sge_o_host", sge_o_host)
        self.account = attr("account", account)
        self.stdout_path_list = attr("stdout_path_list", stdout_path_list)
        self.stderr_path_list = attr("stderr_path_list", stderr_path_list)
        self.mail_list = attr("mail_list", mail_list)
        self.notify = attr("notify", notify)
        self.restart = attr("restart", restart)
        self.env_list = attr("env_list", env_list)
        self.mbind = attr("mbind", mbind)
        self.submit_cmd = attr("submit_cmd", submit_cmd)
        self.exec_host_list = attr("exec_host_list", exec_host_list)
        self.granted_req = attr("granted_req", granted_req)
        self.scheduling = attr("scheduling", scheduling)

        # define status
        self.is_visible = False

    def visible(self):
        self.is_visible = True

    def set_vmem(self, vmem):
        self.reserved_memory = calc_suffix(vmem[self.id.value]) * int(self.slots.value)

    def get_attributes(self):
        if not self.is_visible:
            return None

        return tuple([getattr(self, n) for n in Job.attributes])
