from lib import calc_suffix, add_suffix


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


class StateManager(Coloring):
    required_memory = physical_memory = swapped_memory = False

    def set_child(self, child):
        self.children.append(child)

    def append_children(self, children):
        self.children += children

    def summation_reqmem(self, attr):
        for child in self.children:
            child.summation_reqmem(attr)
        self._get_reserved_memory()

    def _get_reserved_memory(self):
        self.reserved_memory = sum(c.reserved_memory for c in self.children)
        self.rsvmemusage = 0. if calc_suffix(self.memtot) == 0 else self.reserved_memory / calc_suffix(self.memtot)
        self.rsvmem = add_suffix(self.reserved_memory)
