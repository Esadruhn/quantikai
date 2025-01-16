import copy
import math
from dataclasses import dataclass

from quantikai.game import Board, FrozenBoard, Player, Pawns, Colors
from quantikai.bot import minmax
from quantikai.bot import montecarlo


def get_best_move(
    board: Board, current_player: Player, other_player: Player
) -> tuple[int, int, Pawns]:

    # TODO - decide between strategies
    if True:
        best_score, best_move = montecarlo.montecarlo(
            board=board,
            current_player=current_player,
            other_player=other_player,
        )
        print("I am %4.1f%% confident I will win." % (best_score * 100))
    else:
        best_score, best_move = minmax.minmax(
            player_max=current_player.color,
            board=board,
            current_player=current_player,
            other_player=other_player,
        )
        if best_score != 1:
            # because sass is the game
            print("If you play optimally you will win.")
    return best_move
