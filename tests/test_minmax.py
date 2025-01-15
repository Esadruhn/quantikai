"""Tests for `minmax` package."""

import pytest


from quantikai.game_elements import Board, Pawns, Colors, Player
from quantikai import minmax


@pytest.fixture
def fixture_board():
    return Board(
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
        ]
    )


def test_best_move_last():
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [(Pawns.C, Colors.RED), None, None, None],
            [None, (Pawns.D, Colors.RED), None, None],
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
    assert best_move == (0, 3, Pawns.D)


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
    assert best_move != (2, 3, Pawns.B)
