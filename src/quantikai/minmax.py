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


# TODO: proper min max with alpha beta pruning
# TODO: monte carlo
# TODO optimize how to get a possible move from the board


def monte_carlo(
    iterations: int,
    player_max: Colors,
    board: Board,
    current_player: Player,
    other_player: Player,
):
    # IN PROGRESS
    idx = 0
    evaluated_moves = list()
    while 1:
        x = random.randint(len(board.board))
        y = random.randint(len(board.board))
        pawn = list(Pawns)[random.randint(len(Pawns))]

        try:
            current_board = copy.deepcopy(board)
            player = copy.deepcopy(current_player)

            is_a_win = current_board.play(x, y, pawn, current_player.color)
            player.remove(pawn)
            idx += 1
            evaluated_moves.append(())
        except InvalidMoveError:
            pass


def _get_best_move_terminal(
    player_max: Colors,
    moves_to_test: list[tuple[Board, Player, Player, tuple[int, int, Pawns], int]],
) -> tuple[int, int, Pawns]:
    """
    Loosely based on the minmax algorithm, it may choose a move with which it sees a path to victory, not the best one,
    especially in early stages of the game.
    The value of a leaf node is:
    - the maximizer wins = 10
    - the maximizer lose = -10
    There is no draw: if it there is no valid move the player loses

    First call to the function: moves_to_test contains one item: the board, players and None for move and score
    At each iteration, calculate for each item that does not have a score the next moves and score them
    If the move ends the game and the player wins: attribute a +10 score to that move
    If the move ends and the player loses: -10 score to that move
    If the move does not end the party, None score

    If all moves have a score, return the move with the maximum score

    Using terminal recursivity for performance

    Args:
        player_max (Colors): Color of the maximizer: player for whcih we want to find the best move
        moves_to_test (list[tuple[Board, Player, Player, tuple[int, int, Pawns], int]]): _description_

    Returns:
        tuple[int, int, Pawns]: _description_
    """
    new_moves_to_test = list()
    best_move = None
    best_score = -1000

    for board, current_player, other_player, move, score in moves_to_test:
        if score is not None:
            if score > best_score:
                best_score = score
                best_move = move
            continue
        move_children = list()
        ok = True
        for pawn in set(current_player.pawns):
            if not ok:
                break
            for x in range(len(board.board)):
                if not ok:
                    break
                for y in range(len(board.board)):
                    try:
                        current_board = copy.deepcopy(board)
                        player = copy.deepcopy(current_player)

                        is_a_win = current_board.play(x, y, pawn, current_player.color)
                        player.remove(pawn)
                        child_move = (x, y, pawn) if move is None else move
                        if is_a_win:
                            # no need to compute other moves, the perfect player plays this
                            if player_max == current_player.color:
                                return child_move
                            move_children = [
                                (current_board, other_player, player, child_move, -10)
                            ]
                            ok = False
                            break
                        else:
                            # Need to evaluate the move
                            move_children.append(
                                (current_board, other_player, player, child_move, None)
                            )
                    except InvalidMoveError:
                        pass
        # End case if no possible child move: it is a loss for the current player
        if len(move_children) == 0:
            if player_max != current_player.color:
                return child_move
            move_children = [(current_board, other_player, player, move, -10)]

        new_moves_to_test += move_children

    if len(new_moves_to_test) == 0:
        print("return move from no move to test")
        return best_move

    return _get_best_move_terminal(player_max, new_moves_to_test)


def get_best_move(
    board: Board, current_player: Player, other_player: Player
) -> tuple[int, int, Pawns]:
    best_move = _get_best_move_terminal(
        current_player.color, [(board, current_player, other_player, None, None)]
    )
    if best_move is None:
        return None
    return best_move
