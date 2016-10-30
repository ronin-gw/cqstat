from __future__ import print_function
from template import StateManager


class ClusterAttribute(object):
    def rjust(self, l):
        return str(self.value).rjust(l)

    def ljust(self, l):
        return str(self.value).ljust(l)

    def float2(self, l):
        return '{:.2f}'.format(self.value).rjust(l)

    def int(self, l):
        return str(int(self.value)).rjust(l)

    def bytes(self, l, suffix=('', "K", "M", "G")):
        v = self.value
        for s in suffix:
            if v > 1024:
                v /= 1024
            else:
                break
        return "{:3.1f}{}".format(v, s).rjust(l)

    def __init__(self, name, value, strfunc='l'):
        # shortcut: (stringify function, store func)
        STRFUNC_PRESETS = {
            'r': (self.rjust, None),
            'l': (self.ljust, None),
            "f2": (self.float2, float),
            'i': (self.int, float),
            'b': (self.bytes, float)
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
    def update_attrs(cls):
        cls.attributes = ["name", "load", "used", "resv", "avail", "running", "total"]

        if cls.required_memory or cls.physical_memory:
            if cls.physical_memory:
                cls.attributes.append("memuse")
            if cls.required_memory:
                cls.attributes.append("rsvmem")
            cls.attributes.append("memtot")

        if cls.swapped_memory:
            cls.attributes += ["swapus", "swapto"]

        cls.attributes += ["tempd", "mintr"]

        if cls.extra:
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
        error=("\nerror", 'i'),

        memuse=("memory\nusage", 'b'),
        rsvmem=("memory\nreserved", 'b'),
        memtot=("memory\ntotal", 'b'),
        swapus=("swap\nuseage", 'b'),
        swapto=("swap\ntotal", 'b')
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
        self.avail = ClusterAttribute("\navail", int(avail), self.get_avail_strfunc(int(avail), self.running.value))
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

    def get_running_jobs(self):
        return reduce(lambda a, b: a+b, map(lambda q: q.jobs, self.queues))

    def set_host_info(self):
        memtot = sum(q.memtot.value for q in self.queues if q.disabled is False)
        memuse = sum(q.memuse.value for q in self.queues if q.disabled is False)
        swapto = sum(q.swapto.value for q in self.queues if q.disabled is False)
        swapus = sum(q.swapus.value for q in self.queues if q.disabled is False)

        self.memusage = 0. if memtot == 0 else memuse / memtot
        self.swapusage = 0. if swapto == 0 else swapus / swapto

        self.memtot = memtot
        self.memuse = memuse
        self.swapto = swapto
        self.swapus = swapus

    def get_attributes(self):
        return tuple([getattr(self, n, ClusterAttribute(n, None)) for n in Cluster.attributes])

    def get_simple_status(self):
        return (self.name.strfunc(1),
                "{}/{}/{}".format(self.resv.strfunc(1), self.used.strfunc(1), self.running.strfunc(1)),
                "({:3.0f}%)".format(100. * (self.resv.value + self.used.value) / self.running.value))

    def summation_reqmem(self, attr):
        reserved_memory = 0
        for child in self.children:
            child.summation_reqmem(attr)
            reserved_memory += child.reserved_memory
        self.rsvmemusage = 0. if self.memtot.value == 0 else reserved_memory / self.memtot.value
        self.rsvmem = reserved_memory
