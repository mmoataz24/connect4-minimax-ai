from board import AI, HUMAN, create_board, drop_piece, board_to_text
from agent import choose_move
from tree_print import fmt_value


def benchmark():
    board = create_board(6, 7)
    piece = HUMAN
    for c in [3, 3, 2, 4, 2, 3]:
        board = drop_piece(board, c, piece)
        piece = AI if piece == HUMAN else HUMAN
    print("Benchmark board (X = human, O = computer):")
    print(board_to_text(board))
    print()
    print(f"{'K':<4}{'Algorithm':<18}{'Nodes':<12}{'Time (s)':<12}{'Move':<6}{'Value'}")
    print("-" * 60)
    for k in range(1, 7):
        for name in ("minimax", "alphabeta", "expectiminimax"):
            if name == "expectiminimax" and k > 6:
                continue
            col, root, nodes, elapsed = choose_move(board, name, k)
            print(f"{k:<4}{name:<18}{nodes:<12}{elapsed:<12.4f}{col:<6}{fmt_value(root.value)}")
        print("-" * 60)
