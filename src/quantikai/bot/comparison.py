"""Compare the execution time of each method"""

import datetime
import time
import copy
import pathlib
import json

from quantikai.bot import minmax, montecarlo
from quantikai.game import Board, Pawns, Colors, Player, Move

TIMEOUT = 60


def timeit(f, n_iter=100):
    """timeit decorator"""

    def timed(*args, **kw):
        times = list()
        for _ in range(n_iter):
            ts = time.time()
            f(*args, **kw)
            te = time.time()
            times.append(te - ts)
            # TIMEOUT - stop there if it takes too long
            if te - ts > TIMEOUT:
                break
        return round(sum(times) / len(times), 2)

    return timed


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
        tmp_board = copy.deepcopy(board)
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
    times = {
        "n_iter": n_iter,
        "timestamp": datetime.date.today(),
        "montecarlo": dict(),
        "minmax": dict(),
    }
    idx = 0
    result_file = pathlib.Path("bot_algo_time.json")
    current_color = Colors.BLUE
    times["montecarlo"]["args"] = {
        "iterations": 1000,
        "uct_cst": 0.7,
        "use_depth": True,
    }
    times["minmax"]["args"] = {}

    boards, players = init_test_values()
    other_player = players[1]
    for board, player in zip(boards, players):
        if idx >= 4:
            time_res_min = timeit(minmax.get_best_move, n_iter=n_iter)(
                board=board,
                current_player=player,
                other_player=other_player,
                **times["minmax"]["args"]
            )
            times["minmax"][idx] = time_res_min

        tim_res_mont = timeit(montecarlo.get_best_move, n_iter=n_iter)(
            board=board,
            current_player=player,
            other_player=other_player,
            **times["montecarlo"]["args"]
        )
        times["montecarlo"][idx] = tim_res_mont

        # Update the measures at every iteration
        result_file.write_text(json.dumps(times, indent=2))

        idx += 1
        current_color = Colors.BLUE if current_color == Colors.BLUE else Colors.RED
        other_player = player

    return times
