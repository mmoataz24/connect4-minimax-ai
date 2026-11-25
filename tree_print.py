import math


def fmt_value(v):
    if v is None:
        return "-"
    if v == math.inf:
        return "inf"
    if v == -math.inf:
        return "-inf"
    if isinstance(v, float) and v != int(v):
        return f"{v:.2f}"
    return str(int(v))


def node_label(node):
    text = ""
    if node.prob is not None:
        text += f"p={node.prob} "
    if node.move is not None:
        text += f"col {node.move} -> "
    if node.pruned:
        return text + node.kind + "  PRUNED"
    if node.leaf:
        return text + f"LEAF  h={fmt_value(node.value)}"
    text += f"{node.kind}  value={fmt_value(node.value)}"
    if node.note:
        text += "  (reused)"
    if node.best is not None:
        text += f"  best=col {node.best}"
    return text


def build_tree_lines(node, lines, prefix="", is_last=True, is_root=True):
    if is_root:
        lines.append(node_label(node))
        child_prefix = ""
    else:
        lines.append(prefix + ("`-- " if is_last else "|-- ") + node_label(node))
        child_prefix = prefix + ("    " if is_last else "|   ")
    for i, child in enumerate(node.children):
        build_tree_lines(child, lines, child_prefix, i == len(node.children) - 1, False)


def print_tree(root):
    lines = []
    build_tree_lines(root, lines)
    print("\n".join(lines))
