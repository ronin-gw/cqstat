from template import StateManager
from lib import flatten, calc_suffix, add_suffix


class Cluster(StateManager):
    name_len = 0
    used_len = resv_len = tot_len = 0
    memtot_len = rsvmem_len = memuse_len = swapus_len = swapto_len = 0

    def __init__(self, name, cqload, used, res, avail, total, aoacds, cdsue):
        self.queues = self.children = []
        self.set_queue = self.set_child

        self.name = name
        self.cqload = float(cqload) if cqload != "-NA-" else None
        self.used = int(used)
        self.resv = int(res)
        self.avail = int(avail)
        self.tot = int(total)
        self.aoacds = int(aoacds)
        self.cdsue = int(cdsue)

        super(Cluster, self).__init__()

    def apply_queue_stat(self):
        self.used = sum(q.used for q in self.queues if q.disabled is False)
        self.resv = sum(q.resv for q in self.queues if q.disabled is False)
        self.tot = sum(q.tot for q in self.queues if q.disabled is False)
        self.avail = self.tot - self.used
        self.usage = 0. if self.tot == 0 else float(self.used) / self.tot
        self._set_color()

    def set_host_info(self):
        memtot = sum(calc_suffix(q.memtot) for q in self.queues if q.disabled is False)
        memuse = sum(calc_suffix(q.memuse) for q in self.queues if q.disabled is False)
        swapto = sum(calc_suffix(q.swapto) for q in self.queues if q.disabled is False)
        swapus = sum(calc_suffix(q.swapus) for q in self.queues if q.disabled is False)

        self.memusage = 0. if memtot == 0 else memuse / memtot
        self.swapusage = 0. if swapto == 0 else swapus / swapto

        self.memtot = add_suffix(memtot)
        self.memuse = add_suffix(memuse)
        self.swapto = add_suffix(swapto)
        self.swapus = add_suffix(swapus)

        super(Cluster, self).set_host_info()

    def _set_color(self):
        if self.tot < 1:
            self.coloring = self._color("black")
        else:
            self.coloring = self._get_coloring(self.usage,
                                               (0, 0.5, 0.8),
                                               ("blue", "green", "yellow", "red"))

    def set_queue_printlen(self):
        for param in ("memtot", "rsvmem", "memuse", "swapus", "swapto"):
            length = max([len(getattr(q, param, [])) for q in self.queues] + [0])
            if length:
                for q in self.queues:
                    setattr(q, param+"_len", length)

    def has_visible_job(self):
        for queue in self.queues:
            if queue.has_visible_job():
                return True
        return False

    def get_jobids(self):
        return flatten(q.get_jobids() for q in self.queues)

    def _get_r_u_t(self):
        return self.slot_color('{}/{}/{}'.format(str(self.resv).rjust(self.resv_len),
                                                 str(self.used).rjust(self.used_len),
                                                 str(self.tot).rjust(self.tot_len)))

    def print_status(self):
        print "{}  {} ({:3}%){}".format(self.coloring(self.name.rjust(self.name_len)),
                                        self._get_r_u_t(),
                                        int(self.usage*100),
                                        self._get_mem_status())

    def print_simple_status(self):
        print "{}  {} ({:3}%)".format(self.coloring(self.name.rjust(self.name_len)),
                                      self._get_r_u_t(),
                                      int(self.usage*100))

    def get_infolen(self):
        return self.name_len, self.resv_len+self.used_len+self.tot_len+9, self._get_mem_len()
