import math
import random

from board import AI, HUMAN, valid_columns, ordered_columns, drop_piece
from heuristic import heuristic
from node import Node, stats, next_step


def chance_outcomes(board, col):
    cols = valid_columns(board)
    left = (col - 1) in cols
    right = (col + 1) in cols
    if left and right:
        return [(col, 0.6), (col - 1, 0.2), (col + 1, 0.2)]
    if left:
        return [(col, 0.6), (col - 1, 0.4)]
    if right:
        return [(col, 0.6), (col + 1, 0.4)]
    return [(col, 1.0)]


def expectiminimax(board, depth, maximizing, node, cache=None):
    if cache is None:
        cache = {}
    stats["nodes"] += 1
    node.order = next_step()
    key = (tuple(map(tuple, board)), depth, maximizing)
    if key in cache:
        node.value = cache[key]
        node.note = "reused (same board already evaluated)"
        return node.value
    cols = ordered_columns(board)
    if depth == 0 or not cols:
        node.value = heuristic(board)
        node.leaf = True
        cache[key] = node.value
        return node.value
    piece = AI if maximizing else HUMAN
    best = -math.inf if maximizing else math.inf
    for c in cols:
        chance = Node("CHANCE", c, parent=node)
        node.children.append(chance)
        stats["nodes"] += 1
        chance.order = next_step()
        expected = 0
        for real_col, prob in chance_outcomes(board, c):
            child = Node("MIN" if maximizing else "MAX", real_col, prob, parent=chance)
            chance.children.append(child)
            expected += prob * expectiminimax(drop_piece(board, real_col, piece), depth - 1, not maximizing, child, cache)
        chance.value = round(expected, 2)
        if (maximizing and chance.value > best) or (not maximizing and chance.value < best):
            best = chance.value
            node.best = c
    node.value = best
    cache[key] = best
    return best


def real_drop(board, col):
    outcomes = chance_outcomes(board, col)
    cols = [o[0] for o in outcomes]
    probs = [o[1] for o in outcomes]
    return random.choices(cols, weights=probs)[0]
