"""Tests for `minmax` package."""

import pytest


from quantikai.game import Board, Pawns, Colors, Player, Move
from quantikai.bot import minmax


def test_best_move_none():
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
            ],
            [
                (Pawns.C, Colors.RED),
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
            ],
            [
                (Pawns.B, Colors.BLUE),
                (Pawns.D, Colors.RED),
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
            ],
            [
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
            ],
        ]
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
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [None, (Pawns.C, Colors.BLUE), None, None],
            [None, None, None, None],
            [(Pawns.B, Colors.RED), None, None, None],
        ]
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
        board=[
            [
                (Pawns.C, Colors.RED),
                None,
                (Pawns.C, Colors.RED),
                (Pawns.D, Colors.BLUE),
            ],
            [None, (Pawns.B, Colors.BLUE), None, (Pawns.A, Colors.BLUE)],
            [(Pawns.B, Colors.RED), None, (Pawns.A, Colors.BLUE), None],
            [None, None, None, None],
        ]
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
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [(Pawns.C, Colors.RED), None, None, None],
            [None, (Pawns.D, Colors.RED), (Pawns.B, Colors.RED), None],
            [None, None, None, None],
        ]
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
