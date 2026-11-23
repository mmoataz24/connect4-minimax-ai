import math

from board import AI, HUMAN, ordered_columns, drop_piece
from heuristic import heuristic
from node import Node, stats, next_step


def minimax(board, depth, maximizing, node):
    stats["nodes"] += 1
    node.order = next_step()
    cols = ordered_columns(board)
    if depth == 0 or not cols:
        node.value = heuristic(board)
        node.leaf = True
        return node.value
    piece = AI if maximizing else HUMAN
    best = -math.inf if maximizing else math.inf
    for c in cols:
        child = Node("MIN" if maximizing else "MAX", c, parent=node)
        node.children.append(child)
        value = minimax(drop_piece(board, c, piece), depth - 1, not maximizing, child)
        if (maximizing and value > best) or (not maximizing and value < best):
            best = value
            node.best = c
    node.value = best
    return best
