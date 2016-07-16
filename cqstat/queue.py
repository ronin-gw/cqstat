from template import StateManager
from lib import calc_suffix


class Queue(StateManager):
    nodename_len = 0
    nodeinfo_len = None

    def __init__(self, name, qtype, r_u_t, np_load, arch, status=''):
        self.jobs = self.children = []
        self.set_job = self.set_child

        self.name = name
        self.qtype = qtype
        self.resv, self.used, self.tot = map(lambda i: int(i), r_u_t.split('/'))
        self.np_load = np_load
        self.arch = arch
        self.status = status
        if ('d' in self.status) or ('D' in self.status):
            self.disabled = True
        else:
            self.disabled = False

        self.resource, self.hostname = name.split('@')
        self.hostname = self.hostname.split('.')[0]

        if len(self.name) > Queue.nodename_len:
            Queue.nodename_len = len(self.name)

        self.memtot_len = self.rsvmem_len = self.memuse_len = self.swapus_len = self.swapto_len = 0

        super(Queue, self).__init__()

    def set_host_info(self, ncpu, nsoc, ncor, nthr, load, memtot, memuse, swapto, swapus):
        self.ncpu = int(ncpu)
        self.nsoc = int(nsoc)
        self.ncor = int(ncor)
        self.nthr = int(nthr)
        self.load = '0' if load == '-' else load
        self.memtot = memtot
        self.memuse = '0' if memuse == '-' else memuse
        self.swapto = swapto
        self.swapus = '0' if swapus == '-' else swapus

        self.memusage = calc_suffix(self.memuse) / calc_suffix(self.memtot)
        self.swapusage = calc_suffix(self.swapus) / calc_suffix(self.swapto)

        super(Queue, self).set_host_info()

    def _set_color(self):
        self.coloring = self._color()
        self.load_color = self._color()

        if self.status:
            if ('C' in self.status) or ('s' in self.status) or ('S' in self.status):
                self.coloring = self._color("yellow")
            if 'E' in self.status:
                self.coloring = self._color("red")
            if ('a' in self.status) or ('A' in self.status):
                self.coloring = self._color("red")
                self.load_color = self._color("red")
            if self.disabled:
                self.coloring = self._color("black")
        elif self.tot < 1:
            self.coloring = self._color("black")
        else:
            self.coloring = self._get_coloring(self.usage,
                                               (0, 0.5, 0.8),
                                               ("blue", "green", "yellow", "red"))

    def has_visible_job(self):
        for job in self.jobs:
            if job.is_visible is True:
                return True
        return False

    def get_jobids(self):
        return [job.id for job in self.jobs]

    def _get_r_u_t(self):
        return self.slot_color('{}/{}/{}'.format(*map(lambda i: str(i).rjust(2), (self.resv, self.used, self.tot))))

    def print_status(self, indent=0):
        print '\t'*indent + '{} {} {}  {}{}  {}  {}'.format(
            self.coloring(self.name.ljust(Queue.nodename_len)),
            self.qtype.rjust(3),
            self._get_r_u_t(),
            self.load_color(self.np_load.rjust(5)),
            self._get_mem_status(),
            self.arch,
            self.status
        )

    def key(self):
        keys = [self.status,
                float(self.used)/self.tot if self.tot != 0 else 0.,
                self.np_load]

        if Queue.required_memory:
            keys.append(self.rsvmemusage)
        if Queue.physical_memory:
            keys.append(self.memusage)
        if Queue.swapped_memory:
            keys.append(self.swapusage)

        return tuple(keys)

    def get_infolen(self):
        if not Queue.nodeinfo_len:
            Queue.nodeinfo_len = (Queue.nodename_len + len(self.arch) +
                                  self.memtot_len + self.rsvmem_len + self.memuse_len +
                                  self.swapus_len + self.swapto_len + 24)

        return Queue.nodeinfo_len
