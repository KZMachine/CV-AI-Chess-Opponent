import random
from math import inf
from piece import *

def evaluate(board, maximizing_color):
    if maximizing_color.color == WHITE:
        return board.whitescore - board.blackScore
    else:
        return board.blackScore - board.whiteScore


def minimax(board, depth, alpha, beta, maximizing_player, maximizing_color):
    if depth == 0 or board.gameover:
        return None, evaluate(board, maximizing_color)
    moves = board.get_moves()
    best_move = random.choice(moves)
    
    if maximizing_player:
        max_eval = -inf
        for move in moves:
            board.make_move(move[0], move[1])
            current_eval = minimax(board, depth - 1, alpha, beta, False, maximizing_color)[1]
            board.unmake_move()
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break
            return best_move, max_eval
    else:
        min_eval = inf
        for move in moves:
            board.make_move(move[0], move[1])
            current_eval = minimax(board, depth - 1, alpha, beta, True, maximizing_color)[1]
            board.unmake_move()
            if current_eval < min_eval:
                min_eval = current_eval
                best_move = move
            alpha = min(beta, current_eval)
            if beta <= alpha:
                break
            return best_move, min_eval
    
    
