import pytest
import copy

from quantikai.bot.montecarlo import game_tree
from quantikai.bot.montecarlo.main import GameTree, MonteCarloScore
from quantikai.bot.montecarlo.score import DEFAULT_UCT
from quantikai.game import Board, Pawns, Colors, Move
from quantikai.bot.montecarlo.node import Node


@pytest.fixture
def fixture_board():
    return Board(board={(0, 0): (Pawns.A, Colors.BLUE)})


@pytest.fixture
def fixture_parent_node(fixture_board):
    return Node(board=fixture_board.get_frozen(), move_to_play=None)


@pytest.fixture
def fixture_node(fixture_board):
    return Node(
        board=fixture_board.get_frozen(), move_to_play=Move(2, 2, Pawns.A, Colors.RED)
    )


@pytest.fixture
def fixture_game_tree(fixture_board, fixture_parent_node, fixture_node):
    game_tree = GameTree()
    game_tree.add(fixture_parent_node)
    game_tree.add(fixture_node)
    game_tree.add(
        Node(
            board=fixture_board.get_frozen(),
            move_to_play=Move(2, 3, Pawns.A, Colors.RED),
        )
    )
    return game_tree


def test_add_no_parent(fixture_board):
    fixture_node = Node(board=fixture_board.get_frozen(), move_to_play=None)
    game_tree = GameTree()
    game_tree.add(fixture_node)
    score = game_tree.compute_score(fixture_node, parent_node=None)
    assert score == DEFAULT_UCT


def test_add_parent(fixture_game_tree, fixture_parent_node, fixture_node):

    score = fixture_game_tree.compute_score(
        fixture_node, parent_node=fixture_parent_node
    )
    assert score == DEFAULT_UCT


def test_add_parent_visit(fixture_game_tree, fixture_parent_node, fixture_node):

    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    score = fixture_game_tree.compute_score(
        fixture_node, parent_node=fixture_parent_node
    )
    assert score == 1.0


def test_best_move(fixture_board, fixture_game_tree, fixture_parent_node, fixture_node):

    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    fixture_game_tree.compute_score(fixture_parent_node, parent_node=None)
    fixture_game_tree.compute_score(fixture_node, parent_node=fixture_parent_node)

    best_move = fixture_game_tree.get_best_move(fixture_board.get_frozen())
    assert best_move == fixture_node.move_to_play


def test_get_best_play_not_visited(
    fixture_board, fixture_game_tree, fixture_parent_node, fixture_node
):
    best_play = fixture_game_tree.get_best_play(fixture_board.get_frozen(), depth=16)
    assert len(best_play) == 0


def test_get_best_play_max_depth(
    fixture_board, fixture_game_tree, fixture_parent_node, fixture_node
):
    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    fixture_game_tree.compute_score(fixture_parent_node, parent_node=None)
    fixture_game_tree.compute_score(fixture_node, parent_node=fixture_parent_node)

    best_play = fixture_game_tree.get_best_play(fixture_board.get_frozen(), depth=16)
    assert best_play == [
        (fixture_node, MonteCarloScore(times_visited=1, score=1, uct=1.0))
    ]


def test_get_best_play_depth_0(
    fixture_board, fixture_game_tree, fixture_parent_node, fixture_node
):
    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    fixture_game_tree.compute_score(fixture_parent_node, parent_node=None)
    fixture_game_tree.compute_score(fixture_node, parent_node=fixture_parent_node)

    best_play = fixture_game_tree.get_best_play(fixture_board.get_frozen(), depth=0)
    assert best_play == [
        (fixture_node, MonteCarloScore(times_visited=1, score=1, uct=1.0))
    ]


def test_get_best_play_depth_less(
    fixture_board, fixture_game_tree, fixture_parent_node, fixture_node
):
    # stop at depth 0
    frozen = fixture_board.get_frozen()

    fixture_board.play(fixture_node.move_to_play)
    extra_node = Node(
        board=fixture_board.get_frozen(), move_to_play=Move(0, 3, Pawns.C, Colors.BLUE)
    )
    fixture_game_tree.add(extra_node)

    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    fixture_game_tree.update(extra_node, reward=1)

    fixture_game_tree.compute_score(fixture_parent_node, parent_node=None)
    fixture_game_tree.compute_score(fixture_node, parent_node=fixture_parent_node)
    fixture_game_tree.compute_score(extra_node, parent_node=fixture_node)

    best_play = fixture_game_tree.get_best_play(frozen, depth=0)
    assert best_play == [
        (fixture_node, MonteCarloScore(times_visited=1, score=1, uct=1.0))
    ]


def test_get_best_play_depth_1(
    fixture_board, fixture_game_tree, fixture_parent_node, fixture_node
):
    # stop at depth 0
    frozen = fixture_board.get_frozen()
    fixture_board.play(fixture_node.move_to_play)
    extra_node = Node(
        board=fixture_board.get_frozen(), move_to_play=Move(0, 3, Pawns.C, Colors.BLUE)
    )
    fixture_game_tree.add(extra_node)

    fixture_game_tree.update(fixture_parent_node, reward=1)
    fixture_game_tree.update(fixture_node, reward=1)
    fixture_game_tree.update(extra_node, reward=1)

    fixture_game_tree.compute_score(fixture_parent_node, parent_node=None)
    fixture_game_tree.compute_score(fixture_node, parent_node=fixture_parent_node)
    fixture_game_tree.compute_score(extra_node, parent_node=fixture_node)

    best_play = fixture_game_tree.get_best_play(frozen, depth=1)
    assert best_play == [
        (fixture_node, MonteCarloScore(times_visited=1, score=1, uct=1.0)),
        (extra_node, MonteCarloScore(times_visited=1, score=1, uct=1.0)),
    ]


# TODO test get_move_stats
# TODO test to_file and from_file
def test_to_file(fixture_game_tree, tmp_path):
    filepath = tmp_path / "game_tree.json"
    fixture_game_tree.to_file(filepath)

def test_from_file(fixture_game_tree, tmp_path):
    filepath = tmp_path / "game_tree.json"
    fixture_game_tree.to_file(filepath)
    gm = GameTree.from_file(filepath)
    # TODO check gm content
