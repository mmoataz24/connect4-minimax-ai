import math
import time

from node import Node, stats, finalize_tree
from minimax import minimax
from alphabeta import alphabeta
from expectiminimax import expectiminimax


def choose_move(board, algorithm, k):
    stats["nodes"] = 0
    stats["step"] = 0
    root = Node("MAX")
    start = time.time()
    if algorithm == "minimax":
        minimax(board, k, True, root)
    elif algorithm == "alphabeta":
        alphabeta(board, k, -math.inf, math.inf, True, root)
    else:
        expectiminimax(board, k, True, root)
    elapsed = time.time() - start
    steps = []
    finalize_tree(root, steps)
    steps.sort(key=lambda n: n.order)
    root.steps = steps
    return root.best, root, stats["nodes"], elapsed
