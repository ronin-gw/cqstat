from template import Coloring
from lib import calc_suffix


class Job(Coloring):
    def __init__(self, job_ID, prior, name, user, state, s_at_date, s_at_time, slots, ja_task_ID=''):
        self.id = job_ID
        self.prior = float(prior)
        self.name = name
        self.user = user
        self.state = state
        self.s_at_date = s_at_date
        self.s_at_time = s_at_time
        self.slots = int(slots)
        self.a_id = ja_task_ID

        self.is_visible = False

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
