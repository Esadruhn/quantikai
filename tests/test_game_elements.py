#!/usr/bin/env python

"""Tests for `game_elements` package."""
import pytest


from quantikai.game_elements import Board, Pawns, Colors, InvalidMoveError


@pytest.fixture
def fixture_board():
    return Board(board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None]
        ])

@pytest.fixture
def fixture_board_win():
    return Board(board=[
            [(Pawns.A, Colors.BLUE), (Pawns.D, Colors.BLUE), (Pawns.C, Colors.BLUE), None],
            [(Pawns.C, Colors.BLUE), None, None, None],
            [(Pawns.D, Colors.BLUE), None, None, None],
            [None, None, None, None]
        ])

def test_board_negative_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(-1,0,Pawns.A,Colors.BLUE)

def test_board_great_x(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(10,0,Pawns.A,Colors.BLUE)

def test_board_negative_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0,-1,Pawns.A,Colors.BLUE)

def test_board_great_y(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0,10,Pawns.A,Colors.BLUE)

def test_board_piece_already_there(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0,0,Pawns.A,Colors.BLUE)

def test_board_invalid_row(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(0,1,Pawns.A,Colors.RED)

def test_board_invalid_column(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(1,0,Pawns.A,Colors.RED)

def test_board_invalid_section(fixture_board):
    with pytest.raises(InvalidMoveError):
        fixture_board.play(1,1,Pawns.A,Colors.RED)

def test_board_row_win(fixture_board_win):
    assert fixture_board_win.play(0,3,Pawns.B,Colors.BLUE)

def test_board_column_win(fixture_board_win):
    assert fixture_board_win.play(3,0,Pawns.B,Colors.BLUE)

def test_board_section_win(fixture_board_win):
    assert fixture_board_win.play(1,1,Pawns.B,Colors.BLUE)

def test_board_section_bottom_right_win():
    board = Board(board=[
            [(Pawns.B, Colors.RED), (Pawns.A, Colors.RED), (Pawns.B, Colors.RED), None],
            [None, None, None, None],
            [None, None, (Pawns.A, Colors.BLUE), (Pawns.B, Colors.BLUE)],
            [None, None, None, (Pawns.D, Colors.BLUE)]
        ])
    assert board.play(3,2,Pawns.C,Colors.BLUE)

def test_play():
    board = Board()
    board.play(0,0,Pawns["A"], Colors.BLUE)
    board.play(3,3,Pawns["B"], Colors.RED)
    board.play(1,1,Pawns["D"], Colors.BLUE)
    assert board.board == [
        [(Pawns.A, Colors.BLUE), None, None, None],
        [None, (Pawns.D, Colors.BLUE), None, None],
        [None, None, None, None],
        [None, None, None, (Pawns.B, Colors.RED)],         
    ]
