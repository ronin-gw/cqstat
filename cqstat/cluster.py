from __future__ import print_function
from template import Coloring, StateManager
from lib import flatten, calc_suffix, add_suffix


class ClusterAttribute(object):
    def rjust(self, l):
        return str(self.value).rjust(l)

    def ljust(self, l):
        return str(self.value).ljust(l)

    def float2(self, l):
        return '{:.2f}'.format(self.value).rjust(l)

    def int(self, l):
        return str(int(self.value)).rjust(l)

    def __init__(self, name, value, strfunc='l'):
        # shortcut: (stringify function, store func)
        STRFUNC_PRESETS = {
            'r': (self.rjust, None),
            'l': (self.ljust, None),
            "f2": (self.float2, float),
            'i': (self.int, float)
        }

        self.name = name

        if value is None:
            self.strfunc = lambda l: ' '*l
            self.value = "NA"
        elif strfunc in STRFUNC_PRESETS:
            strfunc, valfunc = STRFUNC_PRESETS[strfunc]
            if valfunc is None:
                valfunc = lambda a: a
            self.strfunc = strfunc
            self.value = valfunc(value)
        else:
            self.strfunc = strfunc
            self.value = value


class Cluster(StateManager):
    attributes = ["name", "load", "used", "resv", "avail", "running", "total", "tempd", "mintr"]

    @classmethod
    def enable_ext(cls):
        cls.attributes += ["susm", "susth", "sussub", "suscal", "unknown",
                           "alarm", "mand", "cald", "ambig", "orphan", "error"]

    DEFAULT_FORMS = dict(
        load=("\nload", "f2"),
        used=("\nused", 'i'),
        resv=("\nres", 'i'),
        avail=("\navail", 'i'),
        running=("\nrunning", 'i'),
        total=("\ntotal", 'i'),
        tempd=("temp\ndisabled", 'i'),
        mintr=("manual\nintervention", 'i'),
        susm=("manual\nsuspend", 'i'),
        susth=("suspend\nthreshold", 'i'),
        sussub=("suspend on\nsubordinate", 'i'),
        suscal=("suspend\ncalendar", 'i'),
        unknown=("\nunknow", 'i'),
        alarm=("\nalarm", 'i'),
        mand=("disabled\nmanual", 'i'),
        cald=("disabled\ncalendar", 'i'),
        ambig=("\nambiguous", 'i'),
        orphan=("\norphaned", 'i'),
        error=("\nerror", 'i')
    )

    def __setattr__(self, name, value):
        if name in Cluster.attributes and not isinstance(value, ClusterAttribute):
            label, strfunc = Cluster.DEFAULT_FORMS.get(name, (name, 'l'))
            self.__dict__[name] = ClusterAttribute(label, value, strfunc)
        else:
            self.__dict__[name] = value

    def get_name_strfunc(self, name, colfunc):
        def _f(l):
            if l < 1:
                return name.ljust(l)
            else:
                return colfunc(name.ljust(l))
        return _f

    def get_avail_strfunc(self, a, r):
        def _f(l):
            return "{} ({:3.0f}%)".format(a, 100. * a / r).rjust(l)
        return _f

    def __init__(self, name, load, used, resv, avail, total, tempd, mintr,
                 susm=None, susth=None, sussub=None, suscal=None, unknown=None,
                 alarm=None, mand=None, cald=None, ambig=None, orphan=None, error=None,
                 mem_total=None, mem_used=None, swap_total=None, swap_used=None):

        self.queues = self.children = []
        self.set_queue = self.set_child

        self.running = int(used) + int(avail)
        self.free = float(avail) / self.running.value

        if int(avail) < 1:
            colfunc = self._color("black")
        else:
            colfunc = self._get_coloring(1 - self.free, (0, 0.5, 0.8), ("blue", "green", "yellow", "red"))
        self.name = ClusterAttribute("\nCluster Queue", name, self.get_name_strfunc(name, colfunc))

        self.load = load if load != "-NA-" else None
        self.used = used
        self.resv = resv
        self.avail = ClusterAttribute("\navail", avail, self.get_avail_strfunc(int(avail), self.running.value))
        self.total = total
        self.tempd = tempd
        self.mintr = mintr
        self.susm = susm
        self.susth = susth
        self.sussub = sussub
        self.suscal = suscal
        self.unknown = unknown
        self.alarm = alarm
        self.mand = mand
        self.cald = cald
        self.ambig = ambig
        self.orphan = orphan
        self.error = error

    def get_attributes(self):
        # if not self.is_visible and visible_only:
        #     return None

        return tuple([getattr(self, n, ClusterAttribute(n, None)) for n in Cluster.attributes])

# class Cluster(StateManager):
#     name_len = 0
#     used_len = resv_len = tot_len = 0
#     memtot_len = rsvmem_len = memuse_len = swapus_len = swapto_len = 0
#
#     def __init__(self, name, cqload, used, res, avail, total, aoacds, cdsue):
#         self.queues = self.children = []
#         self.set_queue = self.set_child
#
#         self.name = name
#         self.cqload = float(cqload) if cqload != "-NA-" else None
#         self.used = int(used)
#         self.resv = int(res)
#         self.avail = int(avail)
#         self.tot = int(total)
#         self.aoacds = int(aoacds)
#         self.cdsue = int(cdsue)
#
#         super(Cluster, self).__init__()
#
#     def apply_queue_stat(self):
#         self.used = sum(q.used for q in self.queues if q.disabled is False)
#         self.resv = sum(q.resv for q in self.queues if q.disabled is False)
#         self.tot = sum(q.tot for q in self.queues if q.disabled is False)
#         self.avail = self.tot - self.used
#         self.usage = 0. if self.tot == 0 else float(self.used) / self.tot
#         self._set_color()
#
#     def set_host_info(self):
#         memtot = sum(calc_suffix(q.memtot) for q in self.queues if q.disabled is False)
#         memuse = sum(calc_suffix(q.memuse) for q in self.queues if q.disabled is False)
#         swapto = sum(calc_suffix(q.swapto) for q in self.queues if q.disabled is False)
#         swapus = sum(calc_suffix(q.swapus) for q in self.queues if q.disabled is False)
#
#         self.memusage = 0. if memtot == 0 else memuse / memtot
#         self.swapusage = 0. if swapto == 0 else swapus / swapto
#
#         self.memtot = add_suffix(memtot)
#         self.memuse = add_suffix(memuse)
#         self.swapto = add_suffix(swapto)
#         self.swapus = add_suffix(swapus)
#
#         super(Cluster, self).set_host_info()
#
#     def _set_color(self):
#         if self.tot < 1:
#             self.coloring = self._color("black")
#         else:
#             self.coloring = self._get_coloring(self.usage,
#                                                (0, 0.5, 0.8),
#                                                ("blue", "green", "yellow", "red"))
#
#     def set_queue_printlen(self):
#         for param in ("memtot", "rsvmem", "memuse", "swapus", "swapto"):
#             length = max([len(getattr(q, param, [])) for q in self.queues] + [0])
#             if length:
#                 for q in self.queues:
#                     setattr(q, param+"_len", length)
#
#     def has_visible_job(self):
#         for queue in self.queues:
#             if queue.has_visible_job():
#                 return True
#         return False
#
#     def get_jobids(self):
#         return flatten(q.get_jobids() for q in self.queues)
#
#     def _get_r_u_t(self):
#         return self.slot_color('{}/{}/{}'.format(str(self.resv).rjust(self.resv_len),
#                                                  str(self.used).rjust(self.used_len),
#                                                  str(self.tot).rjust(self.tot_len)))
#
#     def print_status(self):
#         print("{}  {} ({:3}%){}".format(self.coloring(self.name.rjust(self.name_len)),
#                                         self._get_r_u_t(),
#                                         int(self.usage*100),
#                                         self._get_mem_status()))
#
#     def print_simple_status(self):
#         print("{}  {} ({:3}%)".format(self.coloring(self.name.rjust(self.name_len)),
#                                       self._get_r_u_t(),
#                                       int(self.usage*100)))
#
#     def get_infolen(self):
#         return self.name_len, self.resv_len+self.used_len+self.tot_len+9, self._get_mem_len()
