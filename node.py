stats = {"nodes": 0, "step": 0}


class Node:
    __slots__ = ("kind", "move", "prob", "parent", "value", "best", "children", "leaf", "pruned", "note", "order", "last", "steps")

    def __init__(self, kind, move=None, prob=None, parent=None):
        self.kind = kind
        self.move = move
        self.prob = prob
        self.parent = parent
        self.value = None
        self.best = None
        self.children = []
        self.leaf = False
        self.pruned = False
        self.note = ""
        self.order = 0
        self.last = 0


def next_step():
    stats["step"] += 1
    return stats["step"]


def finalize_tree(node, steps):
    steps.append(node)
    node.last = node.order
    for child in node.children:
        finalize_tree(child, steps)
        node.last = max(node.last, child.last)
