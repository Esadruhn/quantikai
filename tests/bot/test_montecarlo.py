"""Tests for `montecarlo` package."""

import copy
import pytest


from quantikai.bot.montecarlo.main import GameTree, _montecarlo_algo
from quantikai.game import Board, Pawns, Colors, Player, Move
from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import MonteCarloScore
from quantikai.bot import montecarlo


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
    _, best_move = montecarlo.get_best_move(board, blue_player, red_player)
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
    _, best_move = montecarlo.get_best_move(board, red_player, blue_player)
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
    _, best_move = montecarlo.get_best_move(board, red_player, blue_player)
    assert best_move != (2, 3, Pawns.B)


def test_best_move_last_full_board():
    # Test with only one possibility
    board = Board(
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.C, Colors.RED),
                (Pawns.C, Colors.RED),
                (Pawns.B, Colors.RED),
                (Pawns.D, Colors.BLUE),
            ],
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.RED),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.D, Colors.RED),
                (Pawns.B, Colors.BLUE),
                (Pawns.A, Colors.RED),
                (Pawns.A, Colors.RED),
            ],
        ]
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
    _, best_move = montecarlo.get_best_move(board, blue_player, red_player)
    assert best_move == Move(0, 3, Pawns.D, Colors.BLUE)


@pytest.mark.parametrize("execution_number", range(10))
def test_best_move_last(execution_number):
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
    _, best_move = montecarlo.get_best_move(board, blue_player, red_player)
    assert best_move == Move(0, 3, Pawns.D, Colors.BLUE), best_move


# TODO add test on game tree directly
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
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.C, Colors.RED),
                (Pawns.C, Colors.RED),
                (Pawns.B, Colors.RED),
                (Pawns.D, Colors.BLUE),
            ],
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.RED),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.D, Colors.RED),
                (Pawns.B, Colors.BLUE),
                (Pawns.A, Colors.RED),
                (Pawns.A, Colors.RED),
            ],
        ]
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
        uct_cst=0.7,
        use_depth=True,
    )
    # TODO: find a board with a small set of moves and assert the game tree
    # is as expected
    nodes = game_tree._game_tree.keys()
    root_node = Node(board=board.get_frozen(), move_to_play=None)
    move_node = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=0, y=3, pawn=Pawns("D"), color=Colors.BLUE),
    )
    assert set(nodes) == {root_node, move_node}
    assert game_tree._game_tree[root_node].is_computed == True
    assert game_tree._game_tree[root_node].is_leaf == False
    assert game_tree._game_tree[root_node].times_visited == 1

    assert game_tree._game_tree[move_node].is_computed == True
    assert game_tree._game_tree[move_node].is_leaf == True
    assert game_tree._game_tree[move_node].times_visited == 1


# TODO add test on game tree directly
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
        board=[
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.B, Colors.BLUE),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.C, Colors.RED),
                (Pawns.C, Colors.RED),
                None,
                (Pawns.D, Colors.BLUE),
            ],
            [
                (Pawns.A, Colors.BLUE),
                (Pawns.D, Colors.RED),
                (Pawns.C, Colors.BLUE),
                None,
            ],
            [
                (Pawns.D, Colors.RED),
                (Pawns.B, Colors.BLUE),
                (Pawns.A, Colors.RED),
                (Pawns.A, Colors.RED),
            ],
        ]
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
        uct_cst=0.7,
        use_depth=True,
    )
    # TODO: find a board with a small set of moves and assert the game tree
    # is as expected
    nodes = game_tree._game_tree.keys()
    root_node = Node(board=board.get_frozen(), move_to_play=None)
    # first move: B RED (1,2) or (2,3)
    red_1 = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=1, y=2, pawn=Pawns("B"), color=Colors.RED),
    )
    red_2 = Node(
        board=board.get_frozen(),
        move_to_play=Move(x=2, y=3, pawn=Pawns("B"), color=Colors.RED),
    )
    board1 = copy.deepcopy(board.board)
    board1[1][2] = (Pawns("B"), Colors.RED)

    board2 = copy.deepcopy(board.board)
    board2[2][3] = (Pawns("B"), Colors.RED)
    # second move: D BLUE (0,3) or ...
    blue_1 = Node(
        board=Board(board1).get_frozen(),
        move_to_play=Move(x=0, y=3, pawn=Pawns("D"), color=Colors.BLUE),
    )
    blue_2 = Node(
        board=Board(board2).get_frozen(),
        move_to_play=Move(x=0, y=3, pawn=Pawns("D"), color=Colors.BLUE),
    )
    # third move: X
    assert set(nodes) == {root_node, red_1, red_2, blue_1, blue_2}
    assert game_tree._game_tree[root_node].is_computed == True
    assert game_tree._game_tree[root_node].is_leaf == False
    assert game_tree._game_tree[root_node].times_visited == 2

    for node in {red_1, red_2}:
        assert game_tree._game_tree[node].is_computed == True
        assert game_tree._game_tree[node].is_leaf == False
        assert game_tree._game_tree[node].times_visited == 1

    for node in {blue_1, blue_2}:
        assert game_tree._game_tree[node].is_computed == True
        assert game_tree._game_tree[node].is_leaf == True
        assert game_tree._game_tree[node].times_visited == 1
