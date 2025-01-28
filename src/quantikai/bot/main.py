import pathlib

from quantikai.bot import montecarlo
from quantikai.game import Board, Move, Player


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
    game_tree_folder: pathlib.Path | None = None,
) -> Move | None:

    return montecarlo.get_best_move(
        board=board,
        current_player=current_player,
        other_player=other_player,
        game_tree_folder=game_tree_folder,
    )
