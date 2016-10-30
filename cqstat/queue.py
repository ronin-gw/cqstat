from __future__ import print_function
from lib import calc_suffix
from template import Coloring, StatAttribute


class QueueAttribute(StatAttribute):
    def bytes(self, l, suffix=('', 'K', 'M', 'G', 'T')):
        v = self.value
        for s in suffix[:-1]:
            if v > 1024:
                v /= 1024
            else:
                break
        else:
            s = suffix[-1]
        return "{:3.1f}{}".format(v, s).rjust(l)


class Queue(Coloring):
    nodename_len = 0
    nodeinfo_len = None

    attributes = ["name", "qtype", "r_u_t", "np_load", "arch", "status"]

    @classmethod
    def update_attrs(cls):
        cls.attributes = ["name", "qtype", "r_u_t", "np_load"]
        if cls.required_memory or cls.physical_memory:
            cls.attributes.append("mem")
        if cls.swapped_memory:
            cls.attributes.append("swap")
        cls.attributes += ["arch", "status"]

    @staticmethod
    def get_colstrfunc(qattr, coloring):
        basefunc = qattr.strfunc

        def _f(l):
            return basefunc(l) if l < 1 else coloring(basefunc(l))

        return _f

    @staticmethod
    def get_static_strfunc(forlen, forstr):
        def _f(l):
            return forlen if l < 1 else forstr
        return _f

    DEFAULT_FORMS = dict(
        qtype=("qtype", 'r'),
        np_load=("np_load", "f2"),
    )

    def __setattr__(self, name, value):
        if name in Queue.attributes and not isinstance(value, QueueAttribute):
            label, strfunc = Queue.DEFAULT_FORMS.get(name, (name, 'l'))
            self.__dict__[name] = QueueAttribute(label, value, strfunc)
        else:
            self.__dict__[name] = value

    def __init__(self, name, qtype, resv, used, total, np_load, arch, status):
        self.jobs = []

        self.name = name
        self.qtype = qtype
        self.resv = QueueAttribute("resv", resv if resv else 0, 'i')
        self.used = QueueAttribute("used", used if used else 0, 'i')
        self.total = QueueAttribute("total", total if total else 0, 'i')
        if self.total.value != 0:
            self.usage = (self.resv.value + self.used.value) / float(self.total.value)
        else:
            self.usage = 0.
        self.np_load = np_load
        self.arch = arch
        self.status = status if status else ''

        if ('d' in self.status.value) or ('D' in self.status.value):
            self.disabled = True
        else:
            self.disabled = False

        self.resource, self.hostname = name.split('@')

        # coloring queue name by status and slot usage
        self.coloring = self._color()
        self.load_color = self._color()

        if status:
            if ('C' in status) or ('s' in status) or ('S' in status):
                self.coloring = self._color("yellow")
            if 'E' in status:
                self.coloring = self._color("red")
            if ('a' in status) or ('A' in status):
                self.coloring = self._color("red")
                self.load_color = self._color("red")
            if self.disabled:
                self.coloring = self._color("black")
        elif self.total.value < 1:
            self.coloring = self._color("black")
        else:
            self.coloring = self._get_coloring(self.usage,
                                               (0, 0.5, 0.8),
                                               ("blue", "green", "yellow", "red"))

        self.name.strfunc = self.get_colstrfunc(self.name, self.coloring)
        self.np_load.strfunc = self.get_colstrfunc(self.np_load, self.load_color)

    def set_job(self, job):
        self.jobs.append(job)

    def append_jobs(self, jobs):
        self.jobs += jobs

    def set_host_info(self, ncpu, nsoc, ncor, nthr, load, memtot, memuse, swapto, swapus):
        self.ncpu = int(ncpu)
        self.nsoc = int(nsoc)
        self.ncor = int(ncor)
        self.nthr = int(nthr)
        self.load = '0' if load == '-' else load
        self.memtot = QueueAttribute("memtot", calc_suffix(memtot), 'b')
        self.memuse = QueueAttribute("memuse", 0. if memuse == '-' else calc_suffix(memuse), 'b')
        self.swapto = QueueAttribute("swapto", calc_suffix(swapto), 'b')
        self.swapus = QueueAttribute("swapus", 0. if swapus == '-' else calc_suffix(swapus), 'b')

        self.memusage = self.memuse.value / self.memtot.value
        self.swapusage = self.swapus.value / self.swapto.value

    def get_rut_len(self):
        return (len(self.resv.strfunc(0)), len(self.used.strfunc(0)), len(self.total.strfunc(0)))

    def set_rut(self, r_len, u_len, t_len):
        r_u_t = "{}/{}/{}".format(self.resv.strfunc(r_len),
                                  self.used.strfunc(u_len),
                                  self.total.strfunc(t_len))
        self.r_u_t = QueueAttribute("resv/used/tot.", r_u_t)
        self.r_u_t.strfunc = self.get_colstrfunc(self.r_u_t,
                                                 self._color() if self.usage < 1 else self._color("red"))

    def get_memory_len(self):
        return {
            k: len(getattr(self, a).strfunc(0))
            for k, a, arg in (("use_len", "memuse", Queue.physical_memory),
                              ("rsv_len", "rsvmem", Queue.required_memory),
                              ("tot_len", "memtot", True))
            if arg is True
        }

    def set_memory_attrs(self, tot_len, use_len=None, rsv_len=None):
        if use_len:
            use_color = self._get_coloring(self.memusage, (0.5, 0.8), (None, "yellow", "red"))
            tot_color = use_color
        if rsv_len:
            rsv_color = self._get_coloring(self.rsvmemusage, (0.5, 0.8), (None, "yellow", "red"))
            tot_color = rsv_color

        if use_len and rsv_len:
            self.mem = "{}/{}/{}".format(self.memuse.strfunc(use_len),
                                         self.rsvmem.strfunc(rsv_len),
                                         self.memtot.strfunc(tot_len))
            colored = "{}/{}/{}".format(use_color(self.memuse.strfunc(use_len)),
                                        rsv_color(self.rsvmem.strfunc(rsv_len)),
                                        tot_color(self.memtot.strfunc(tot_len)))
        else:
            self.mem = "{}/{}".format(
                self.rsvmem.strfunc(rsv_len) if rsv_len else self.memuse.strfunc(use_len),
                self.memtot.strfunc(tot_len)
            )
            colored = "{}/{}".format(
                rsv_color(self.rsvmem.strfunc(rsv_len)) if rsv_len else use_color(self.memuse.strfunc(use_len)),
                tot_color(self.memtot.strfunc(tot_len))
            )

        self.mem.strfunc = self.get_static_strfunc(self.mem.value, colored)

    def get_swap_len(self):
        return [len(self.swapus.strfunc(0)), len(self.swapto.strfunc(0))] if Queue.swapped_memory else []

    def set_swap_attrs(self, us_len, to_len):
        swap_color = self._get_coloring(self.swapusage, (0.5, 0.8), (None, "yellow", "red"))
        self.swap = "{}/{}".format(self.swapus.strfunc(us_len),
                                   self.swapto.strfunc(to_len))
        colored = "{}/{}".format(swap_color(self.swapus.strfunc(us_len)),
                                 swap_color(self.swapto.strfunc(to_len)))
        self.swap.strfunc = self.get_static_strfunc(self.swap.value, colored)

    def summation_reqmem(self, attr):
        reserved_memory = 0
        for job in self.jobs:
            job.summation_reqmem(attr)
            reserved_memory += job.reserved_memory
        self.rsvmemusage = 0. if self.memtot.value == 0 else reserved_memory / self.memtot.value
        self.rsvmem = QueueAttribute("rsvmem", reserved_memory, 'b')

    def get_attributes(self):
        return tuple([getattr(self, n, QueueAttribute(n, None)) for n in Queue.attributes])

    def has_visible_job(self):
        for job in self.jobs:
            if job.is_visible is True:
                return True
        return False

    def key(self):
        keys = [self.status.value,
                float(self.used.value)/self.total.value if self.total.value != 0 else 0.,
                self.np_load.value]

        if Queue.required_memory:
            keys.append(self.rsvmemusage)
        if Queue.physical_memory:
            keys.append(self.memusage)
        if Queue.swapped_memory:
            keys.append(self.swapusage)

        return tuple(keys)
