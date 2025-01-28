"""Tests for `minmax` package."""

import pytest


from quantikai.game import Board, Pawns, Colors, Player, Move
from quantikai.bot import minmax


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
    best_move = minmax.get_best_move(board, blue_player, red_player)
    assert best_move is None


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
    best_move = minmax.get_best_move(board, red_player, blue_player)
    assert best_move is not None
    assert best_move != (1, 0, Pawns.D)
    assert best_move != (2, 0, Pawns.C)
    assert best_move != (2, 0, Pawns.D)


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
    best_move = minmax.get_best_move(board, red_player, blue_player)
    assert best_move != Move(2, 3, Pawns.B, Colors.RED)


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
    best_move = minmax.get_best_move(board, blue_player, red_player)
    assert best_move == Move(0, 3, Pawns.D, Colors.BLUE)
