from enum import Enum, auto

TITLE = "Model Checker"
OBJ_NAME = "modelChecker"

INFO_SYMBOL = "\u24D8" # Unicode for 'ⓘ'


class Severity(Enum):
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    BLOCKING = 4

    def __ge__(self, other):
        if isinstance(other, Severity):
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Severity):
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Severity):
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Severity):
            return self.value < other.value
        return NotImplemented


PASS_COLOR = "#446644"

SEVERITY_COLORS = {
    Severity.MILD: "#666644",        
    Severity.MODERATE: "#777711",
    Severity.SEVERE: "#884444",
    Severity.BLOCKING: "#552222",
}

class NodeType(Enum):
    UV = auto()
    VERTEX = auto()
    EDGE = auto()
    FACE = auto()
    NODE = auto()


EXPANDED_LABEL = '\u2193'
COLLAPSED_LABEL = '\u21B5'


COMPONENT_MAPPING = {
            NodeType.UV: ".map[{}]",
            NodeType.VERTEX: ".vtx[{}]",
            NodeType.EDGE: ".e[{}]",
            NodeType.FACE: ".f[{}]",
         }
