#!/usr/bin/env python

"""Tests for `game` package."""
import pytest


from quantikai.game import Board, Pawns, Colors, InvalidMoveError


@pytest.fixture
def fixture_board():
    return Board(
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
        ]
    )


@pytest.fixture
def fixture_board_win_first():
    return Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [(Pawns.C, Colors.BLUE), None, None, None],
            [(Pawns.D, Colors.BLUE), None, None, None],
            [None, None, None, None],
        ]
    )


@pytest.fixture
def fixture_board_win_last():
    return Board(
        board=[
            [None, None, None, None],
            [None, None, None, (Pawns.B, Colors.BLUE)],
            [None, None, None, (Pawns.C, Colors.BLUE)],
            [
                None,
                (Pawns.C, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
            ],
        ]
    )


def test_board_negative_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(-1, 0, Pawns.A, Colors.BLUE)


def test_board_great_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(10, 0, Pawns.A, Colors.BLUE)


def test_board_negative_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0, -1, Pawns.A, Colors.BLUE)


def test_board_great_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0, 10, Pawns.A, Colors.BLUE)


def test_board_piece_already_there(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0, 0, Pawns.A, Colors.BLUE)


@pytest.mark.parametrize(
    "row_idx, column_idx", [(i, j) for i in range(1, 4) for j in range(0, 4)]
)
def test_board_invalid_row(row_idx, column_idx):
    board = Board(
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
            [(Pawns.A, Colors.BLUE), None, None, None],
        ]
    )
    with pytest.raises(InvalidMoveError):
        board.play(row_idx, column_idx, Pawns.A, Colors.RED)


@pytest.mark.parametrize(
    "row_idx, column_idx", [(i, j) for i in range(0, 4) for j in range(1, 4)]
)
def test_board_invalid_column(row_idx, column_idx):
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
            ],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
        ]
    )
    with pytest.raises(InvalidMoveError):
        board.play(row_idx, column_idx, Pawns.A, Colors.RED)


@pytest.mark.parametrize(
    "pawn,row_idx, column_idx", [("A", 1, 1), ("B", 0, 3), ("C", 3, 0), ("D", 2, 2)]
)
def test_board_invalid_section(pawn, row_idx, column_idx):
    board = Board(
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [None, None, (Pawns.B, Colors.BLUE), None],
            [None, (Pawns.C, Colors.BLUE), None, None],
            [None, None, None, (Pawns.D, Colors.BLUE)],
        ]
    )
    with pytest.raises(InvalidMoveError):
        board.play(row_idx, column_idx, Pawns[pawn], Colors.RED)


def test_board_row_win(fixture_board_win_first):
    assert fixture_board_win_first.play(0, 3, Pawns.B, Colors.BLUE)


def test_board_column_win(fixture_board_win_first):
    assert fixture_board_win_first.play(3, 0, Pawns.B, Colors.BLUE)


def test_board_section_win(fixture_board_win_first):
    assert fixture_board_win_first.play(1, 1, Pawns.B, Colors.BLUE)


def test_board_row_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(3, 0, Pawns.A, Colors.BLUE)


def test_board_column_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(0, 3, Pawns.A, Colors.BLUE)


def test_board_section_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(2, 2, Pawns.A, Colors.BLUE)


def test_board_section_bottom_right_win():
    board = Board(
        board=[
            [(Pawns.B, Colors.RED), (Pawns.A, Colors.RED), (Pawns.B, Colors.RED), None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), (Pawns.B, Colors.BLUE)],
            [None, None, None, (Pawns.D, Colors.BLUE)],
        ]
    )
    assert board.play(3, 2, Pawns.C, Colors.BLUE)


def test_move_is_not_win():
    board = Board(
        board=[
            [(Pawns.B, Colors.RED), (Pawns.A, Colors.RED), (Pawns.B, Colors.RED), None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), (Pawns.B, Colors.BLUE)],
            [None, None, None, (Pawns.D, Colors.BLUE)],
        ]
    )
    assert not board.play(3, 2, Pawns.A, Colors.BLUE)
    assert not board.play(0, 3, Pawns.C, Colors.RED)


def test_play():
    board = Board()
    board.play(0, 0, Pawns["A"], Colors.BLUE)
    board.play(3, 3, Pawns["B"], Colors.RED)
    board.play(1, 1, Pawns["D"], Colors.BLUE)
    assert board.board == [
        [(Pawns.A, Colors.BLUE), None, None, None],
        [None, (Pawns.D, Colors.BLUE), None, None],
        [None, None, None, None],
        [None, None, None, (Pawns.B, Colors.RED)],
    ]


def test_have_possible_move():
    board = Board(
        board=[
            [(Pawns.B, Colors.RED), (Pawns.A, Colors.RED), (Pawns.B, Colors.RED), None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), (Pawns.B, Colors.BLUE)],
            [None, None, None, (Pawns.D, Colors.BLUE)],
        ]
    )
    assert board.have_possible_move(Colors.RED)
    assert board.have_possible_move(Colors.RED)


def test_no_possible_move_full_board():
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.C, Colors.RED),
                (Pawns.B, Colors.RED),
                (Pawns.B, Colors.RED),
            ],
            [
                (Pawns.B, Colors.RED),
                (Pawns.C, Colors.RED),
                (Pawns.B, Colors.RED),
                (Pawns.B, Colors.RED),
            ],
            [
                (Pawns.B, Colors.RED),
                (Pawns.D, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
            ],
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
            ],
        ]
    )
    assert not board.have_possible_move(Colors.RED)


def test_no_valid_move():
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                (Pawns.B, Colors.RED),
                (Pawns.B, Colors.RED),
            ],
            [
                (Pawns.B, Colors.RED),
                None,
                (Pawns.B, Colors.RED),
                (Pawns.B, Colors.BLUE),
            ],
            [
                (Pawns.B, Colors.RED),
                (Pawns.D, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
            ],
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.BLUE),
            ],
        ]
    )
    assert not board.have_possible_move(Colors.RED)


def test_get_possible_moves():
    board = Board(
        board=[
            [None, (Pawns.A, Colors.RED), None, None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), None],
            [None, None, None, (Pawns.B, Colors.RED)],
        ]
    )
    moves = board.get_possible_moves([Pawns.A], color=Colors.BLUE)
    assert moves == {
        (1, 2, Pawns.A, Colors.BLUE),
        (1, 3, Pawns.A, Colors.BLUE),
        (2, 0, Pawns.A, Colors.BLUE),
        (2, 3, Pawns.A, Colors.BLUE),
        (3, 0, Pawns.A, Colors.BLUE),
        (3, 2, Pawns.A, Colors.BLUE),
    }


def test_get_possible_moves_pawns():
    board = Board(
        board=[
            [None, (Pawns.A, Colors.RED), None, None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), None],
            [None, None, None, (Pawns.B, Colors.RED)],
        ]
    )
    moves = board.get_possible_moves([Pawns.A, Pawns.B], color=Colors.BLUE)
    a_moves = {
        (1, 2, Pawns.A, Colors.BLUE),
        (1, 3, Pawns.A, Colors.BLUE),
        (2, 0, Pawns.A, Colors.BLUE),
        (2, 3, Pawns.A, Colors.BLUE),
        (3, 0, Pawns.A, Colors.BLUE),
        (3, 2, Pawns.A, Colors.BLUE),
    }
    b_moves = {
        (0, 0, Pawns.B, Colors.BLUE),
        (0, 2, Pawns.B, Colors.BLUE),
        (1, 0, Pawns.B, Colors.BLUE),
        (1, 1, Pawns.B, Colors.BLUE),
        (1, 2, Pawns.B, Colors.BLUE),
        (2, 0, Pawns.B, Colors.BLUE),
        (2, 1, Pawns.B, Colors.BLUE),
    }
    assert moves == a_moves | b_moves


def test_get_possible_move_edge_case():
    board = Board(
        [
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [(Pawns.C, Colors.RED), (Pawns.C, Colors.RED), None, (Pawns.A, Colors.RED)],
            [
                (Pawns.B, Colors.BLUE),
                (Pawns.D, Colors.RED),
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.RED),
            ],
            [None, None, (Pawns.C, Colors.BLUE), None],
        ]
    )
    board.print()
    move = (3, 0, Pawns.D, Colors.BLUE)
    moves = board.get_possible_moves([Pawns.D], Colors.BLUE)
    assert move not in moves


def test_get_possible_moves_optimize_empty_board():
    board = Board()
    moves = board.get_possible_moves(
        pawns=list(Pawns), color=Colors.BLUE, optimize=True
    )
    assert moves == {
        (0, 0, Pawns.A, Colors.BLUE),
        (0, 1, Pawns.A, Colors.BLUE),
        (1, 0, Pawns.A, Colors.BLUE),
        (1, 1, Pawns.A, Colors.BLUE),
    }


def test_get_possible_moves_optimize_one():
    board = Board()
    board.play(0, 0, Pawns.A, Colors.RED)
    moves = board.get_possible_moves(
        pawns=list(Pawns), color=Colors.BLUE, optimize=True
    )
    same_pawn_moves = {
        (2, 1, Pawns.A, Colors.BLUE),
        (3, 1, Pawns.A, Colors.BLUE),
        (2, 2, Pawns.A, Colors.BLUE),
        (2, 3, Pawns.A, Colors.BLUE),
        (3, 2, Pawns.A, Colors.BLUE),
        (3, 3, Pawns.A, Colors.BLUE),
    }
    assert same_pawn_moves.issubset(moves)
    other_pawn_moves = moves - same_pawn_moves
    positions = {(x, y) for (x, y, _, _) in other_pawn_moves}
    assert positions == {
        # bottom left section
        (2, 0),
        (2, 1),
        (3, 0),
        (3, 1),
        # upper left section
        (0, 1),
        (1, 0),
        (1, 1),
        # bottom right section
        (2, 2),
        (2, 3),
        (3, 2),
        (3, 3),
    }
