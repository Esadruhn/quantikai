from quantikai.game import Board, Player, Move
from quantikai.bot import montecarlo


def get_best_move(board: Board, current_player: Player, other_player: Player) -> Move:

    best_move = montecarlo.get_best_move(
        board=board,
        current_player=current_player,
        other_player=other_player,
    )
    return best_move
