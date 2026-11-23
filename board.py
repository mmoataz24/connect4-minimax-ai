EMPTY = 0
HUMAN = 1
AI = 2
windows_cache = {}


def create_board(rows, cols):
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def copy_board(board):
    return [row[:] for row in board]


def valid_columns(board):
    return [c for c in range(len(board[0])) if board[0][c] == EMPTY]


def ordered_columns(board):
    center = len(board[0]) // 2
    return sorted(valid_columns(board), key=lambda c: abs(c - center))


def next_open_row(board, col):
    for r in range(len(board) - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def drop_piece(board, col, piece):
    new_board = copy_board(board)
    new_board[next_open_row(new_board, col)][col] = piece
    return new_board


def is_full(board):
    return len(valid_columns(board)) == 0


def get_windows(rows, cols):
    if (rows, cols) in windows_cache:
        return windows_cache[(rows, cols)]
    windows = []
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
                end_r = r + 3 * dr
                end_c = c + 3 * dc
                if 0 <= end_r < rows and 0 <= end_c < cols:
                    windows.append([(r + i * dr, c + i * dc) for i in range(4)])
    windows_cache[(rows, cols)] = windows
    return windows


def count_fours(board, piece):
    count = 0
    for window in get_windows(len(board), len(board[0])):
        if all(board[r][c] == piece for r, c in window):
            count += 1
    return count


def is_playable(board, r, c):
    return r == len(board) - 1 or board[r + 1][c] != EMPTY


def board_to_text(board):
    symbols = {EMPTY: ".", HUMAN: "X", AI: "O"}
    lines = []
    for row in board:
        lines.append(" ".join(symbols[x] for x in row))
    lines.append(" ".join(str(c % 10) for c in range(len(board[0]))))
    return "\n".join(lines)
