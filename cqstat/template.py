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

    def __init__(self):
        if self.tot == 0:
            self.usage = 0.
        else:
            self.usage = float(self.used) / self.tot

        self._set_color()
        self._set_slot_color()

        self.rsvmem_color = self._color()
        self.mem_color = self._color()
        self.swap_color = self._color()

    def set_child(self, child):
        self.children.append(child)

    def set_vmem(self, vmem_dict):
        for child in self.children:
            child.set_vmem(vmem_dict)
        self._get_reserved_memory()

    def _get_reserved_memory(self):
        self.reserved_memory = sum(c.reserved_memory for c in self.children)
        self.rsvmemusage = 0. if calc_suffix(self.memtot) == 0 else self.reserved_memory / calc_suffix(self.memtot)
        self.rsvmem = add_suffix(self.reserved_memory)
        self._set_rsvmem_color()

    def _update_len(self, attrs):
        for attr in attrs:
            length = len(str(getattr(self, attr)))
            maxlen = len(str(getattr(self, attr+"_len", '')))
            if length > maxlen:
                setattr(self, attr+"_len", length)

    def set_host_info(self):
        self._set_mem_color()
        self._set_swap_color()

    def _set_slot_color(self):
        self.slot_color = self._color()
        if self.usage == 1:
            self.slot_color = self._color("red")

    def _set_mem_color(self):
        self.mem_color = self._get_coloring(self.memusage,
                                            (0.01, 0.5, 0.8),
                                            (None, None, "yellow", "red"))

    def _set_swap_color(self):
        self.swap_color = self._get_coloring(self.swapusage,
                                             (0.01, 0.5, 0.8),
                                             (None, None, "yellow", "red"))

    def _set_rsvmem_color(self):
        self.rsvmem_color = self._get_coloring(self.rsvmemusage,
                                               (0.01, 0.5, 0.8),
                                               (None, None, "yellow", "red"))

    def _get_mem_status(self):
        memstats = []

        mem = ''
        if self.physical_memory and self.required_memory:
            mem = (self.mem_color(self.memuse.rjust(self.memuse_len)) + '/' +
                   self.rsvmem_color(self.rsvmem.rjust(self.rsvmem_len)) + '/' +
                   self.rsvmem_color(self.memtot.rjust(self.memtot_len)))
        elif self.physical_memory:
            mem = self.mem_color(self.memuse.rjust(self.memuse_len) + '/' +
                                 self.memtot.ljust(self.memtot_len))
        elif self.required_memory:
            mem = self.rsvmem_color(self.rsvmem.rjust(self.rsvmem_len) + '/' +
                                    self.memtot.rjust(self.memtot_len))

        if mem:
            memstats.append(mem)

        if self.swapped_memory:
            memstats.append(self.swap_color(self.swapus.rjust(self.swapus_len) + '/' +
                            self.swapto.rjust(self.swapto_len)))

        if memstats:
            return "  {}".format("  ".join(memstats))
        else:
            return ''

    def _get_mem_len(self):
        l = 0
        if self.physical_memory and self.required_memory:
            l += self.memuse_len + self.rsvmem_len + self.memtot_len + 2
        elif self.physical_memory:
            l += self.memuse_len + self.memtot_len + 1
        elif self.required_memory:
            l += self.rsvmem_len + self.memtot_len + 1

        if l != 0:
            l += 2

        if self.swapped_memory:
            l += self.swapus_len + self.swapto_len + 3

        return l
