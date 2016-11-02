import datetime


class Coloring(object):
    COLOR = dict(red='\033[91m', yellow='\033[93m', green='\033[92m', blue='\033[94m', black='\033[90m')
    ENDC = '\033[0m'
    enable = True

    def _color(self, col=None):
        if (not col) or (not self.enable):
            return lambda text: text
        else:
            return lambda text: self.COLOR[col] + text + self.ENDC

    def _get_coloring(self, value, thresholds, colorset):
        for th, col in zip(sorted(thresholds), colorset):
            if value <= th:
                return self._color(col)
        else:
            return self._color(colorset[-1])


class StatAttribute(Coloring):
    def rjust(self, l):
        return str(self.value).rjust(l)

    def center(self, l):
        return str(self.value).center(l)

    def ljust(self, l):
        return str(self.value).ljust(l)

    @classmethod
    def sliceljust(cls, v):
        if cls.name_length < 1:
            return str(v)
        else:
            return str(v)[:cls.name_length]

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

    @staticmethod
    def store_datetime(val):
        try:
            return datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            # try parsing without msec
            try:
                return datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                # try store value as epoch
                return datetime.datetime.fromtimestamp(float(val) / 1000)

    def second(self, l):
        m, s = divmod(self.value, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return "{:02.0f}:{:02.0f}:{:02.0f}:{:02.0f}".format(d, h, m, s).rjust(l)

    def fsecond(self, l):
        return "{:7.5f}".format(l).rjust(l)

    def bytes(self, l, suffix=('B ', "KB", "MB", "GB")):
        v = self.value
        for s in suffix:
            if v >= 1024:
                v /= 1024
            else:
                break
        return "{:7.5f} {}".format(v, s).rjust(l)

    def bytesec(self, l):
        return self.bytes(l, suffix=('Bs ', "KBs", "MBs", "GBs"))

    def __init__(self, name, value, strfunc='l'):
        # shortcut: (stringify function, store func)
        STRFUNC_PRESETS = {
            'r': (self.rjust, None),
            'c': (self.center, None),
            'l': (self.ljust, None),
            "sl": (self.ljust, self.sliceljust),
            "f5": (self.float5, float),
            "f2": (self.float2, float),
            'i': (self.int, float),
            "state": (self.state, None),
            'd': (self.datetime, self.store_datetime),
            "sec": (self.second, float),
            "fsec": (self.fsecond, float),
            'b': (self.bytes, float),
            "bs": (self.bytes, float)
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
