import copy
import random
from dataclasses import dataclass

from quantikai.game_elements import Board, Player, InvalidMoveError, Pawns, Colors


@dataclass
class Node:
    board: Board
    current_player: Player
    other_player: Player


@dataclass
class MinMaxNode(Node):
    is_max: bool  # this is the maximizer's turn
    score: int = None

# TODO: monte carlo
# TODO optimize how to get a possible move from the board

def minmax(
    player_max: Colors, board: Board, current_player: Player, other_player: Player, depth=0, max_depth=3,
) -> tuple[int, tuple[int, int, Pawns, Colors]]:

    # TODO: heuristics and exploit board symmetry to never need this
    if depth == max_depth:
        return 0, None

    possible_moves = board.get_possible_moves(
        current_player.pawns, current_player.color
    )
    if len(possible_moves) == 0:
        if current_player.color == player_max:
            return -1, None
        return 1, None

    best_move = None
    best_score = None
    for move in possible_moves:
        tmp_board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)
        is_a_win = tmp_board.play(*move)
        tmp_player.remove(move[2])

        move_score = None
        if is_a_win and tmp_player.color == player_max:
            move_score = 1
        if is_a_win and tmp_player.color != player_max:
            move_score = -1
        if not is_a_win:
            move_score, _ = minmax(
                player_max=player_max,
                board=tmp_board,
                current_player=other_player,
                other_player=tmp_player,
                depth=depth+1,
            )

        if tmp_player.color == player_max:
            # Maximise the score
            if best_score is None or best_score < move_score:
                best_move = move
                best_score = move_score
                # break and do not evaluate other moves if is max
                if best_score == 1:
                    break
        else:
            # Minimize the score
            if best_score is None or best_score > move_score:
                best_move = move
                best_score = move_score
                # break and do not evaluate other moves if is min
                if best_score == -1:
                    break
    return (best_score, best_move)


def get_best_move(
    board: Board, current_player: Player, other_player: Player
) -> tuple[int, int, Pawns]:

    best_score, best_move = minmax(
        player_max=current_player.color,
        board=board,
        current_player=current_player,
        other_player=other_player,
    )
    return best_move
