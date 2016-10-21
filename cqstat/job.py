from template import Coloring
from lib import calc_suffix


class Job(Coloring):
    def __init__(
        self,
        job_ID,
        prior,
        name,
        user,
        state,
        jclass,
        nurg=None,
        nprior=None,
        ntckts=None,
        urg=None,
        rrcontr=None,
        wtcontr=None,
        dicontr=None,
        ppri=None,
        uid=None,
        group=None,
        gid=None,
        sup_group=None,
        project=None,
        department=None,
        sub_strt_at=None,
        sub_at=None,
        strt_at=None,
        deadline=None,
        wallclock=None,
        cpu=None,
        mem=None,
        io=None,
        low=None,
        loops=None,
        vmem=None,
        max_vmem=None,
        tckts=None,
        ovrts=None,
        ovrts=None,
        otckt=None,
        ftckt=None,
        stckt=None,
        share=None,
        queue=None,
        slots=None,
        ja_task_id=None,
        master_q=None,
        h_resources=None,
        master_h_res=None,
        s_resources=None,
        binding=None,
        sge_o_home=None,
        sge_o_log_name=None,
        sge_o_path=None,
        sge_o_shell=None,
        sge_o_workdir=None,
        sge_o_host=None,
        account=None,
        stdout_path_list=None,
        stderr_path_list=None,
        mail_list=None,
        notify=None,
        restart=None,
        env_list=None,
        mbind=None,
        submit_cmd=None,
        exec_host_list=None,
        granted_req=None,
        scheduling=None
    ):
        pass

    def visible(self):
        self.is_visible = True

    def set_vmem(self, vmem):
        self.reserved_memory = calc_suffix(vmem[self.id]) * self.slots

    def get_status(self, indent=0):
        if not self.is_visible:
            return None

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

        return (
            self.id.ljust(8),
            self.prior,
            self.name.ljust(10),
            self.user.center(12),
            coloring(self.state.rjust(3)),
            self.s_at_date,
            self.s_at_time,
            str(self.slots).rjust(5),
            self.a_id
        )

    def print_status(self, indent=0):
        if self.is_visible:
            print '\t'*indent + "{} {:.5f} {} {}  {}  {} {} {} {}".format(*self.get_status(indent))
