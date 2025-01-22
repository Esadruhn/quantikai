from quantikai.game import Board, Player, Pawns
from quantikai.bot import minmax
from quantikai.bot import montecarlo


def _switch_montecarlo_minmax(
    board: Board, current_player: Player, other_player: Player
):
    # Decide between strategies
    # Each player starts with 8 pawns, so we deduce from that the number of pawns on the board
    # Safer method would be to count on the board
    nb_pawns_on_board = 16 - len(current_player.pawns) - len(other_player.pawns)
    if nb_pawns_on_board <= 4:
        return montecarlo.get_best_move
    return minmax.get_best_move


def get_best_move(
    board: Board, current_player: Player, other_player: Player
) -> tuple[int, int, Pawns]:

    _, best_move = _switch_montecarlo_minmax(
        board=board, current_player=current_player, other_player=other_player
    )(
        board=board,
        current_player=current_player,
        other_player=other_player,
    )
    return best_move
