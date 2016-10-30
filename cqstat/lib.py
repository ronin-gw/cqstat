import re
import sys
if sys.version_info > (3, ):
    from functools import reduce


def calc_suffix(num):
    suf = dict(K=1024, M=1048576, G=1073741824, T=1099511627776)
    if num[-1] not in "KMGTkmgt":
        return float(num)
    else:
        return float(num[:-1]) * suf[num[-1].upper()]


def generate_pattern(names):
    patterns = []
    for name in names:
        p = name.replace('*', ".*").replace('?', ".?")
        try:
            re.compile(p)
        except re.error:
            continue

        patterns.append(p)

    if patterns:
        return re.compile('(' + ")|(".join(patterns) + ')')
    else:
        return Re_dummy(False)


class Re_dummy(object):
    def __init__(self, default):
        self.default = default

    def match(self, *args, **kwargs):
        return self.default


def flatten(lists_in_list):
    return reduce(lambda a, b: a+b, lists_in_list, list())


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
