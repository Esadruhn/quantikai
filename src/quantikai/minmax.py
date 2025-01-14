import copy

from quantikai.game_elements import Board, Player, InvalidMoveError, Pawns, Colors


def _get_best_move_terminal(player_max: Colors, moves_to_test: list[tuple[Board, Player, Player, tuple[int, int, Pawns], int]]) -> tuple[int, int, Pawns]:
    """
    Based on the minmax algorithm: expect both players to play perfectly
    The value of a leaf node is:
    - the maximizer wins = 10
    - the maximizer lose = -10
    There is no draw: if it there is no valid move the player loses
    The value of a node is equal to the max (if maximizer) value of its children or min if is the minimizer's turn

    First call to the function: moves_to_test contains one item: the board, players and None for move and score
    At each iteration, calculate for each item that does not have a score the next moves and score them
    If the move ends the game and the player wins: attribute a +10 score to that move 
    If the move ends and the player loses: -10 score to that move
    If the move does not end the party, None score

    If all moves have a score, return the move with the maximum score
    TODO: check that the assert is never triggered, we expect that this happens only when evaluating the maximizer next possible move

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
            if not ok: break
            for x in range(0, len(board.board)):
                if not ok: break
                for y in range(0, len(board.board)):
                    try:
                        current_board = copy.deepcopy(board)
                        player = copy.deepcopy(current_player)

                        is_a_win = current_board.play(x, y, pawn, current_player.color)
                        player.remove(pawn)
                        child_move = (x,y,pawn) if move is None else move
                        if is_a_win:
                            # no need to compute other moves, the perfect player plays this
                            move_score = 10 if player_max == current_player.color else -10
                            move_children = [(current_board, other_player, player, child_move, move_score)]
                            ok = False
                            break
                        else:
                            # Need to evaluate the move
                            move_children.append((current_board, other_player, player, child_move, None))
                    except InvalidMoveError:
                        pass
        # End case if no possible child move: it is a loss for the current player
        if len(move_children) == 0:
            move_score = -10 if player_max == current_player.color else 10
            move_children = [(current_board, other_player, player, move, move_score)]

        new_moves_to_test += move_children

    if len(new_moves_to_test) == 0:
        assert current_player.color == player_max, "We should be at the maximizer's turn."
        return best_move

    return _get_best_move_terminal(player_max, new_moves_to_test)

def get_best_move(board: Board, current_player: Player, other_player: Player) -> tuple[int, int, Pawns]:
    best_move = _get_best_move_terminal(current_player.color, [(board, current_player, other_player, None, None)])
    if best_move is None: return None
    return best_move