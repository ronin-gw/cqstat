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
    def set_child(self, child):
        self.children.append(child)

    def append_children(self, children):
        self.children += children
