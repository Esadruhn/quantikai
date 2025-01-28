import pathlib

from quantikai.game import Board, Player, Move
from quantikai.bot import montecarlo


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
    game_tree_file: pathlib.Path | None,
) -> Move:

    best_move = montecarlo.get_best_move(
        board=board,
        current_player=current_player,
        other_player=other_player,
        game_tree_file=game_tree_file,
    )
    return best_move
