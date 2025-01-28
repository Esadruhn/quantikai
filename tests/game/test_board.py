#!/usr/bin/env python

"""Tests for `game` package."""
import pytest


from quantikai.game import Board, Move, Pawns, Colors, InvalidMoveError


@pytest.fixture
def fixture_board():
    return Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (1, 0): (Pawns.A, Colors.BLUE),
            (2, 0): (Pawns.A, Colors.BLUE),
            (3, 0): (Pawns.A, Colors.BLUE),
        }
    )


@pytest.fixture
def fixture_board_win_first():
    return Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.D, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            (1, 0): (Pawns.C, Colors.BLUE),
            (2, 0): (Pawns.D, Colors.BLUE),
        }
    )


@pytest.fixture
def fixture_board_win_last():
    return Board(
        board={
            (1, 3): (Pawns.B, Colors.BLUE),
            (2, 3): (Pawns.C, Colors.BLUE),
            (3, 1): (Pawns.C, Colors.BLUE),
            (3, 2): (Pawns.B, Colors.BLUE),
            (3, 3): (Pawns.D, Colors.BLUE),
        }
    )


@pytest.fixture
def fixture_board_1():
    return Board(
        board={
            (0, 0): (Pawns.B, Colors.RED),
            (0, 1): (Pawns.A, Colors.RED),
            (0, 2): (Pawns.B, Colors.RED),
            (2, 2): (Pawns.A, Colors.BLUE),
            (2, 3): (Pawns.B, Colors.BLUE),
            (3, 3): (Pawns.D, Colors.BLUE),
        }
    )


def test_board_negative_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(-1, 0, Pawns.A, Colors.BLUE))


def test_board_great_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(10, 0, Pawns.A, Colors.BLUE))


def test_board_negative_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(0, -1, Pawns.A, Colors.BLUE))


def test_board_great_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(0, 10, Pawns.A, Colors.BLUE))


def test_board_piece_already_there(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(0, 0, Pawns.A, Colors.BLUE))


@pytest.mark.parametrize(
    "row_idx, column_idx", [(i, j) for i in range(1, 4) for j in range(0, 4)]
)
def test_board_invalid_row(fixture_board, row_idx, column_idx):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(Move(row_idx, column_idx, Pawns.A, Colors.RED))


@pytest.mark.parametrize(
    "row_idx, column_idx", [(i, j) for i in range(0, 4) for j in range(1, 4)]
)
def test_board_invalid_column(row_idx, column_idx):
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.A, Colors.BLUE),
            (0, 2): (Pawns.A, Colors.BLUE),
            (0, 3): (Pawns.A, Colors.BLUE),
        }
    )
    with pytest.raises(InvalidMoveError):
        board.play(Move(row_idx, column_idx, Pawns.A, Colors.RED))


@pytest.mark.parametrize(
    "pawn,row_idx, column_idx", [("A", 1, 1), ("B", 0, 3), ("C", 3, 0), ("D", 2, 2)]
)
def test_board_invalid_section(pawn, row_idx, column_idx):
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (1, 2): (Pawns.B, Colors.BLUE),
            (2, 1): (Pawns.C, Colors.BLUE),
            (3, 3): (Pawns.D, Colors.BLUE),
        }
    )
    with pytest.raises(InvalidMoveError):
        board.play(Move(row_idx, column_idx, Pawns[pawn], Colors.RED))


def test_board_row_win(fixture_board_win_first):
    assert fixture_board_win_first.play(Move(0, 3, Pawns.B, Colors.BLUE))


def test_board_column_win(fixture_board_win_first):
    assert fixture_board_win_first.play(Move(3, 0, Pawns.B, Colors.BLUE))


def test_board_section_win(fixture_board_win_first):
    assert fixture_board_win_first.play(Move(1, 1, Pawns.B, Colors.BLUE))


def test_board_row_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(Move(3, 0, Pawns.A, Colors.BLUE))


def test_board_column_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(Move(0, 3, Pawns.A, Colors.BLUE))


def test_board_section_win_last(fixture_board_win_last):
    assert fixture_board_win_last.play(Move(2, 2, Pawns.A, Colors.BLUE))


def test_board_section_bottom_right_win(fixture_board_1):
    assert fixture_board_1.play(Move(3, 2, Pawns.C, Colors.BLUE))


def test_move_is_not_win(fixture_board_1):
    assert not fixture_board_1.play(Move(3, 2, Pawns.A, Colors.BLUE))
    assert not fixture_board_1.play(Move(0, 3, Pawns.C, Colors.RED))


def test_play():
    board = Board()
    board.play(Move(0, 0, Pawns.A, Colors.BLUE))
    board.play(Move(3, 3, Pawns.B, Colors.RED))
    board.play(Move(1, 1, Pawns.D, Colors.BLUE))
    assert board.board == {
        (0, 0): (Pawns.A, Colors.BLUE),
        (3, 3): (Pawns.B, Colors.RED),
        (1, 1): (Pawns.D, Colors.BLUE),
    }


def test_have_possible_move(fixture_board_1):
    assert fixture_board_1.have_possible_move(Colors.BLUE)
    assert fixture_board_1.have_possible_move(Colors.RED)


def test_no_possible_move_full_board():
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
    assert not board.have_possible_move(Colors.RED)


def test_no_valid_move():
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.C, Colors.BLUE),
            (0, 2): (Pawns.B, Colors.RED),
            (0, 3): (Pawns.B, Colors.RED),
            (1, 0): (Pawns.B, Colors.RED),
            # (1,1) is empty
            (1, 2): (Pawns.B, Colors.RED),
            (1, 3): (Pawns.B, Colors.BLUE),
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
    assert not board.have_possible_move(Colors.RED)


def test_get_possible_moves():
    board = Board(
        board={
            (0, 1): (Pawns.A, Colors.RED),
            (2, 2): (Pawns.A, Colors.BLUE),
            (3, 3): (Pawns.B, Colors.RED),
        }
    )
    moves = board.get_possible_moves([Pawns.A], color=Colors.BLUE)
    assert moves == {
        Move(1, 2, Pawns.A, Colors.BLUE),
        Move(1, 3, Pawns.A, Colors.BLUE),
        Move(2, 0, Pawns.A, Colors.BLUE),
        Move(2, 3, Pawns.A, Colors.BLUE),
        Move(3, 0, Pawns.A, Colors.BLUE),
        Move(3, 2, Pawns.A, Colors.BLUE),
    }


def test_get_possible_moves_pawns():
    board = Board(
        board={
            (0, 1): (Pawns.A, Colors.RED),
            (2, 2): (Pawns.A, Colors.BLUE),
            (3, 3): (Pawns.B, Colors.RED),
        }
    )
    moves = board.get_possible_moves([Pawns.A, Pawns.B], color=Colors.BLUE)
    a_moves = {
        Move(1, 2, Pawns.A, Colors.BLUE),
        Move(1, 3, Pawns.A, Colors.BLUE),
        Move(2, 0, Pawns.A, Colors.BLUE),
        Move(2, 3, Pawns.A, Colors.BLUE),
        Move(3, 0, Pawns.A, Colors.BLUE),
        Move(3, 2, Pawns.A, Colors.BLUE),
    }
    b_moves = {
        Move(0, 0, Pawns.B, Colors.BLUE),
        Move(0, 2, Pawns.B, Colors.BLUE),
        Move(1, 0, Pawns.B, Colors.BLUE),
        Move(1, 1, Pawns.B, Colors.BLUE),
        Move(1, 2, Pawns.B, Colors.BLUE),
        Move(2, 0, Pawns.B, Colors.BLUE),
        Move(2, 1, Pawns.B, Colors.BLUE),
    }
    assert moves == a_moves | b_moves


def test_get_possible_move_edge_case():
    board = Board(
        board={
            (0, 0): (Pawns.A, Colors.BLUE),
            (0, 1): (Pawns.B, Colors.BLUE),
            (0, 2): (Pawns.C, Colors.BLUE),
            (1, 0): (Pawns.C, Colors.RED),
            (1, 1): (Pawns.C, Colors.RED),
            (1, 3): (Pawns.A, Colors.RED),
            (2, 0): (Pawns.B, Colors.BLUE),
            (2, 1): (Pawns.D, Colors.RED),
            (2, 2): (Pawns.A, Colors.BLUE),
            (2, 3): (Pawns.D, Colors.RED),
            (3, 2): (Pawns.C, Colors.BLUE),
        }
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
        Move(0, 0, Pawns.A, Colors.BLUE),
        Move(0, 1, Pawns.A, Colors.BLUE),
        Move(1, 1, Pawns.A, Colors.BLUE),
    }


def test_get_possible_moves_optimize_one():
    board = Board()
    board.play(Move(0, 0, Pawns.A, Colors.RED))
    moves = board.get_possible_moves(
        pawns=list(Pawns), color=Colors.BLUE, optimize=True
    )
    same_pawn_moves = {
        Move(2, 1, Pawns.A, Colors.BLUE),
        Move(3, 1, Pawns.A, Colors.BLUE),
        Move(2, 2, Pawns.A, Colors.BLUE),
        Move(2, 3, Pawns.A, Colors.BLUE),
        Move(3, 2, Pawns.A, Colors.BLUE),
        Move(3, 3, Pawns.A, Colors.BLUE),
    }
    assert same_pawn_moves.issubset(moves)
    other_pawn_moves = moves - same_pawn_moves
    positions = {(m.x, m.y) for m in other_pawn_moves}
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


def test_get_possible_moves_optimize_one_section_1():
    board = Board({(0, 1): (Pawns.A, Colors.RED)})
    moves = board.get_possible_moves(
        pawns=list(Pawns), color=Colors.BLUE, optimize=True
    )
    same_pawn_moves = {
        Move(2, 0, Pawns.A, Colors.BLUE),
        Move(3, 0, Pawns.A, Colors.BLUE),
        Move(2, 2, Pawns.A, Colors.BLUE),
        Move(2, 3, Pawns.A, Colors.BLUE),
        Move(3, 2, Pawns.A, Colors.BLUE),
        Move(3, 3, Pawns.A, Colors.BLUE),
    }
    assert same_pawn_moves.issubset(moves)
    other_pawn_moves = moves - same_pawn_moves
    positions = {(m.x, m.y) for m in other_pawn_moves}
    assert positions == {
        # bottom left section
        (2, 0),
        (2, 1),
        (3, 0),
        (3, 1),
        # upper left section
        (0, 0),
        (1, 0),
        (1, 1),
        # bottom right section
        (2, 2),
        (2, 3),
        (3, 2),
        (3, 3),
    }
