from board import AI, HUMAN, is_full, count_fours, get_windows, is_playable


def heuristic(board):
    rows, cols = len(board), len(board[0])
    if is_full(board):
        return (count_fours(board, AI) - count_fours(board, HUMAN)) * 1000
    score = 0
    for window in get_windows(rows, cols):
        ai = 0
        human = 0
        empty_cell = None
        for r, c in window:
            if board[r][c] == AI:
                ai += 1
            elif board[r][c] == HUMAN:
                human += 1
            else:
                empty_cell = (r, c)
        if ai and human:
            continue
        if ai == 4:
            score += 1000
        elif human == 4:
            score -= 1000
        elif ai == 3:
            score += 80 if is_playable(board, empty_cell[0], empty_cell[1]) else 50
        elif human == 3:
            score -= 100 if is_playable(board, empty_cell[0], empty_cell[1]) else 60
        elif ai == 2:
            score += 10
        elif human == 2:
            score -= 12
        elif ai == 1:
            score += 1
        elif human == 1:
            score -= 1
    center = cols // 2
    for r in range(rows):
        if board[r][center] == AI:
            score += 4
        elif board[r][center] == HUMAN:
            score -= 4
    return score
