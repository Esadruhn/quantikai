"""Tests for `montecarlo` package."""

import copy

from quantikai.bot import montecarlo
from quantikai.bot.montecarlo.main import _montecarlo_algo
from quantikai.bot.montecarlo.node import Node
from quantikai.game import Board, Colors, Move, Pawns, Player


def test_best_move_none():
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.C, Colors.RED),
            (0, 2): (Pawns.B, Colors.RED),
            (0, 3): (Pawns.B, Colors.RED),
            (1, 0): (Pawns.B, Colors.RED),
            (1, 1): (Pawns.C, Colors.RED),
            (1, 2): (Pawns.B, Colors.RED),
            (1, 3): (Pawns.B, Colors.RED),
            (2, 0): (Pawns.B, Colors.RED),
            (2, 1): (Pawns.D, Colors.BLUE),
            (2, 2): (Pawns.A, Colors.BLUE),
            (2, 3): (Pawns.B, Colors.BLUE),
            (3, 0): (Pawns.A, Colors.BLUE),
            (3, 1): (Pawns.D, Colors.BLUE),
            (3, 2): (Pawns.A, Colors.BLUE),
            (3, 3): (Pawns.D, Colors.BLUE),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    best_move = montecarlo.get_best_move(board, blue_player, red_player)
    assert best_move is None


def test_best_move_last_full_board():
    # Test with only one possibility
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.B, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            # (0, 3): None
            (1, 0): (Pawns.C, Colors.RED),
            (1, 1): (Pawns.C, Colors.RED),
            (1, 2): (Pawns.B, Colors.RED),
            (1, 3): (Pawns.D, Colors.BLUE),
            (2, 0): (Pawns.A, Colors.BLUE),
            (2, 1): (Pawns.D, Colors.RED),
            (2, 2): (Pawns.C, Colors.BLUE),
            # (2, 3): None
            (3, 0): (Pawns.D, Colors.RED),
            (3, 1): (Pawns.B, Colors.BLUE),
            (3, 2): (Pawns.A, Colors.RED),
            (3, 3): (Pawns.A, Colors.RED),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.B,
        ],
    )
    best_move = montecarlo.get_best_move(board, blue_player, red_player)
    assert best_move == Move(0, 3, Pawns.D, Colors.BLUE)


# Add test on the game tree directly
# Complexity is too high not to test inner workings
def test_montecarlo_algo():
    #          0     1     2     3
    #        ____  ____   ____  ____
    #     0 |_Ab_||_Bb_| |_Cb_||____|
    #     1 |_Cr_||_Cr_| |_Br_||_Db_|
    #        ____  ____   ____  ____
    #     2 |_Ab_||_Dr_| |_Cb_||____|
    #     3 |_Dr_||_Bb_| |_Ar_||_Ar_|
    # Test with only one possibility
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.B, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            # (0, 3): None
            (1, 0): (Pawns.C, Colors.RED),
            (1, 1): (Pawns.C, Colors.RED),
            (1, 2): (Pawns.B, Colors.RED),
            (1, 3): (Pawns.D, Colors.BLUE),
            (2, 0): (Pawns.A, Colors.BLUE),
            (2, 1): (Pawns.D, Colors.RED),
            (2, 2): (Pawns.C, Colors.BLUE),
            # (2, 3): None
            (3, 0): (Pawns.D, Colors.RED),
            (3, 1): (Pawns.B, Colors.BLUE),
            (3, 2): (Pawns.A, Colors.RED),
            (3, 3): (Pawns.A, Colors.RED),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.B,
        ],
    )
    game_tree = _montecarlo_algo(
        board=board,
        current_player=blue_player,
        other_player=red_player,
        iterations=1,
        use_depth=True,
    )
    nodes = game_tree._game_tree.keys()
    root_node = Node(board=board.get_frozen(), move_to_play=None)
    move_node = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=0, y=3, pawn=Pawns("D"), color=Colors.BLUE),
    )
    assert set(nodes) == {root_node, move_node}
    for node in nodes:
        assert game_tree._game_tree[node].times_visited == 1


# Add test on the game tree directly
# Complexity is too high not to test inner workings
def test_montecarlo_algo_depth_2():
    #          0     1     2     3
    #        ____  ____   ____  ____
    #     0 |_Ab_||_Bb_| |_Cb_||____|
    #     1 |_Cr_||_Cr_| |____||_Db_|
    #        ____  ____   ____  ____
    #     2 |_Ab_||_Dr_| |_Cb_||____|
    #     3 |_Dr_||_Bb_| |_Ar_||_Ar_|
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.B, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            # (0, 3): None
            (1, 0): (Pawns.C, Colors.RED),
            (1, 1): (Pawns.C, Colors.RED),
            # (1, 2): (None
            (1, 3): (Pawns.D, Colors.BLUE),
            (2, 0): (Pawns.A, Colors.BLUE),
            (2, 1): (Pawns.D, Colors.RED),
            (2, 2): (Pawns.C, Colors.BLUE),
            # (2, 3): None
            (3, 0): (Pawns.D, Colors.RED),
            (3, 1): (Pawns.B, Colors.BLUE),
            (3, 2): (Pawns.A, Colors.RED),
            (3, 3): (Pawns.A, Colors.RED),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.B,
            Pawns.B,
        ],
    )
    game_tree = _montecarlo_algo(
        board=board,
        current_player=red_player,
        other_player=blue_player,
        iterations=2,
        use_depth=True,
    )

    nodes = game_tree._game_tree.keys()
    root_node = Node(board=board.get_frozen(), move_to_play=None)

    # first move: B RED (1,2) or (2,3)
    red_1 = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=1, y=2, pawn=Pawns("B"), color=Colors.RED),
    )
    # winning move
    red_2 = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=2, y=3, pawn=Pawns("B"), color=Colors.RED),
    )
    board1 = copy.deepcopy(board)
    board1.play(red_1.move_to_play)

    board2 = copy.deepcopy(board)
    board2.play(red_2.move_to_play)

    # second move: D BLUE (0,3)
    # winning move
    blue_1 = Node(
        board=board1.get_frozen(),
        move_to_play=Move(x=0, y=3, pawn=Pawns("D"), color=Colors.BLUE),
    )
    assert set(nodes) == {root_node, red_1, red_2, blue_1}

    assert game_tree._game_tree[root_node].times_visited == 2

    for node in {red_1, red_2, blue_1}:
        assert game_tree._game_tree[node].times_visited == 1


def test_worst_move():
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (1, 1): (Pawns.C, Colors.BLUE),
            (3, 0): (Pawns.B, Colors.RED),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    best_move = montecarlo.get_best_move(board, red_player, blue_player)
    assert best_move is not None
    assert best_move != Move(1, 0, Pawns.D, Colors.RED)
    assert best_move != Move(2, 0, Pawns.C, Colors.RED)
    assert best_move != Move(2, 0, Pawns.D, Colors.RED)


def test_best_move_1():
    board = Board(
        board={
            (0, 0): (Pawns.C, Colors.RED),
            (0, 2): (Pawns.C, Colors.RED),
            (0, 3): (Pawns.D, Colors.BLUE),
            (1, 1): (Pawns.B, Colors.BLUE),
            (1, 3): (Pawns.A, Colors.BLUE),
            (2, 0): (Pawns.B, Colors.RED),
            (2, 2): (Pawns.A, Colors.BLUE),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.B,
            Pawns.C,
            Pawns.C,
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.A,
            Pawns.A,
            Pawns.B,
            Pawns.D,
            Pawns.D,
        ],
    )
    best_move = montecarlo.get_best_move(board, red_player, blue_player)
    assert best_move != (2, 3, Pawns.B)


def test_best_move_last():
    #          0     1     2     3
    #        ____  ____   ____  ____
    #     0 |__A_||__B_| |__C_||____|
    #     1 |__C_||____| |____||____|
    #        ____  ____   ____  ____
    #     2 |____||__D_| |__B_||____|
    #     3 |____||____| |____||____|
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.B, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            (1, 0): (Pawns.C, Colors.RED),
            (2, 1): (Pawns.D, Colors.RED),
            (2, 2): (Pawns.B, Colors.RED),
        }
    )
    blue_player = Player(
        color=Colors.BLUE,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    red_player = Player(
        color=Colors.RED,
        pawns=[
            Pawns.A,
            Pawns.B,
            Pawns.C,
            Pawns.D,
        ],
    )
    best_move = montecarlo.get_best_move(board, blue_player, red_player)
    assert best_move == Move(0, 3, Pawns.D, Colors.BLUE), best_move


# TODO
# test get_best_move with a game tree file
# test get_best_play with a game tree file
# test get_move_stats with a game tree file
