import re


def calc_suffix(num):
    suf = dict(K=1024, M=1048576, G=1073741824, T=1099511627776)
    if num[-1] not in "KMGTkmgt":
        return float(num)
    else:
        return float(num[:-1]) * suf[num[-1].upper()]


def add_suffix(num):
    for suf, vol in (('K', 1024), ('M', 1048576), ('G', 1073741824), ('T', 1099511627776)):
        if vol <= num < vol*1024:
            return "{:.1f}{}".format(num/vol, suf)

    return "{:.1f}".format(num)


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
