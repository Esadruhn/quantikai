"""Compare the execution time of each method"""

import datetime
import copy
import pathlib
import json
import timeit

from quantikai.bot import minmax, montecarlo
from quantikai.game import Board, Pawns, Colors, Player, Move


def init_test_values():
    """Get boards and players states - will keep only board
    where it's blue's turn to play
    """

    board = Board()
    blue_player = Player(color=Colors.BLUE)
    red_player = Player(color=Colors.RED)

    boards = [board]
    players = [blue_player, red_player]
    current_player = blue_player

    moves = [
        Move(0, 0, Pawns.A, Colors.BLUE),
        Move(1, 0, Pawns.C, Colors.RED),
        Move(0, 1, Pawns.B, Colors.BLUE),
        Move(1, 1, Pawns.C, Colors.RED),
        Move(0, 2, Pawns.C, Colors.BLUE),
        Move(1, 2, Pawns.B, Colors.RED),
        Move(2, 0, Pawns.A, Colors.BLUE),
        Move(2, 1, Pawns.D, Colors.RED),
        Move(2, 2, Pawns.C, Colors.BLUE),
        Move(3, 2, Pawns.A, Colors.RED),
        Move(3, 1, Pawns.B, Colors.BLUE),
        Move(3, 0, Pawns.D, Colors.RED),
        Move(1, 3, Pawns.D, Colors.BLUE),
        Move(3, 3, Pawns.A, Colors.RED),
    ]
    for move in moves:
        tmp_board: Board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)

        tmp_board.play(move)
        tmp_player.remove(move.pawn)
        boards.append(tmp_board)
        players.append(tmp_player)

        board = tmp_board
        current_player = players[len(players) - 2]
    return boards, players


def get_method_times():

    n_iter = 10
    n_repeat = 5

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    times = {
        "n_iter": n_iter,
        "n_repeat": n_repeat,
        "timestamp": timestamp,
        "montecarlo": dict(),
        "minmax": dict(),
    }
    idx = 0
    result_file = pathlib.Path("bot_algo_time_" + timestamp + ".json")
    current_color = Colors.BLUE
    times["montecarlo"]["args"] = {
        "iterations": 10000,
        "use_depth": True,
    }
    times["minmax"]["args"] = {}

    boards, players = init_test_values()
    other_player = players[1]
    for board, player in zip(boards, players):
        if idx >= 4:
            d = timeit.Timer(
                lambda: minmax.get_best_move(
                    board=board,
                    current_player=player,
                    other_player=other_player,
                    **times["minmax"]["args"]
                )
            )
            times["minmax"][idx] = round(min(d.repeat(n_repeat, n_iter)) / n_iter, 2)

        d = timeit.Timer(
            lambda: montecarlo.get_best_move(
                board=board,
                current_player=player,
                other_player=other_player,
                **times["montecarlo"]["args"]
            )
        )
        times["montecarlo"][idx] = round(min(d.repeat(n_repeat, n_iter)) / n_iter, 2)

        # Update the measures at every iteration
        result_file.write_text(json.dumps(times, indent=2))

        idx += 1
        current_color: Colors = (
            Colors.RED if current_color == Colors.BLUE else Colors.BLUE
        )
        other_player: Player = player

    return times
