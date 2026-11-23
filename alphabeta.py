import math

from board import AI, HUMAN, ordered_columns, drop_piece
from heuristic import heuristic
from node import Node, stats, next_step
from tree_print import fmt_value


def alphabeta(board, depth, alpha, beta, maximizing, node):
    stats["nodes"] += 1
    node.order = next_step()
    cols = ordered_columns(board)
    if depth == 0 or not cols:
        node.value = heuristic(board)
        node.leaf = True
        return node.value
    piece = AI if maximizing else HUMAN
    best = -math.inf if maximizing else math.inf
    for i, c in enumerate(cols):
        child = Node("MIN" if maximizing else "MAX", c, parent=node)
        node.children.append(child)
        value = alphabeta(drop_piece(board, c, piece), depth - 1, alpha, beta, not maximizing, child)
        if maximizing:
            if value > best:
                best = value
                node.best = c
            alpha = max(alpha, best)
        else:
            if value < best:
                best = value
                node.best = c
            beta = min(beta, best)
        if alpha >= beta:
            for p in cols[i + 1:]:
                pruned = Node("MIN" if maximizing else "MAX", p, parent=node)
                pruned.pruned = True
                pruned.order = next_step()
                pruned.note = f"alpha = {fmt_value(alpha)} >= beta = {fmt_value(beta)}"
                node.children.append(pruned)
            break
    node.value = best
    return best
