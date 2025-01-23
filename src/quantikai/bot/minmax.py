import copy

from quantikai.game import Board, Player, Pawns, Colors, Move


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
) -> tuple[int, Move]:
    return _recursive_minmax(
        player_max=current_player.color,
        board=board,
        current_player=current_player,
        other_player=other_player,
    )


def _recursive_minmax(
    player_max: Colors,
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 0,
) -> tuple[int, tuple[int, int, Pawns, Colors]]:
    """

    Args:
        player_max (Colors):
        board (Board):
        current_player (Player):
        other_player (Player):
        depth (int, optional): Leave it at 0, it is updated during the recursion. Defaults to 0.

    Returns:
        tuple[int, tuple[int, int, Pawns, Colors]]:
    """

    possible_moves = board.get_possible_moves(
        current_player.pawns,
        current_player.color,
        optimize=True,
    )
    if len(possible_moves) == 0:
        if current_player.color == player_max:
            return -1, None
        return 1, None

    best_move = None
    best_score = None
    # If no winning move in sight, we try to drag the game
    # so that the opponent may make a mistake
    # TODO: test
    best_depth = None
    for move in possible_moves:
        tmp_board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)
        is_a_win = tmp_board.play(move)
        tmp_player.remove(move.pawn)

        move_score = None
        if is_a_win and tmp_player.color == player_max:
            move_score = 1
        if is_a_win and tmp_player.color != player_max:
            move_score = -1
        if not is_a_win:
            move_score, _ = _recursive_minmax(
                player_max=player_max,
                board=tmp_board,
                current_player=other_player,
                other_player=tmp_player,
                depth=depth + 1,
            )

        if tmp_player.color == player_max:
            # Maximise the score
            if best_score is None or best_score < move_score:
                best_move = move
                best_score = move_score
                best_depth = depth
                # break and do not evaluate other moves if is max
                if best_score == 1:
                    break
            elif best_score == move_score and depth > best_depth:
                best_move = move
                best_depth = depth
        else:
            # Minimize the score
            if best_score is None or best_score > move_score:
                best_move = move
                best_score = move_score
                best_depth = depth
                # break and do not evaluate other moves if is min
                if best_score == -1:
                    break
            elif best_score == move_score and depth > best_depth:
                best_move = move
                best_depth = depth
    return (best_score, best_move)
