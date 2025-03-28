import pytest

from quantikai.bot.montecarlo.main import GameTree, MonteCarloScore
from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import DEFAULT_UCT
from quantikai.game import Board, Colors, Move, Pawns


@pytest.fixture
def board():
    return Board(board={(0, 0): (Pawns.A, Colors.BLUE)})


@pytest.fixture
def parent_node(board):
    return Node(board=board.get_frozen(), move_to_play=None)


@pytest.fixture
def node(board):
    return Node(
        board=board.get_frozen(), move_to_play=Move(2, 2, Pawns.A, Colors.RED)
    )


@pytest.fixture
def game_tree(board, parent_node, node):
    game_tree = GameTree()
    game_tree.add(parent_node)
    game_tree.add(node)
    game_tree.add(
        Node(
            board=board.get_frozen(),
            move_to_play=Move(2, 3, Pawns.A, Colors.RED),
        )
    )
    return game_tree


def test_add_no_parent(board):
    node = Node(board=board.get_frozen(), move_to_play=None)
    game_tree = GameTree()
    game_tree.add(node)
    score = game_tree.compute_score(node)
    assert score == DEFAULT_UCT


def test_add_parent(game_tree, node):

    score = game_tree.compute_score(node)
    assert score == DEFAULT_UCT


def test_add_parent_visit(game_tree, parent_node, node):

    game_tree.update(parent_node, reward=1)
    game_tree.compute_score(node)
    game_tree.update(node, reward=1)
    score = game_tree.compute_score(node)
    assert score == 1.0


def test_best_move(board, game_tree, parent_node, node):

    game_tree.update(parent_node, reward=1)
    game_tree.compute_score(node)
    game_tree.update(node, reward=1)

    best_move = game_tree.get_best_move(board.get_frozen())
    assert best_move == node.move_to_play


def test_get_best_play_not_visited(board, game_tree, parent_node, node):
    best_play = game_tree.get_best_play(board.get_frozen(), depth=16)
    assert len(best_play) == 0


def test_get_best_play_max_depth(board, game_tree, parent_node, node):
    game_tree.update(parent_node, reward=1)
    game_tree.compute_score(node)
    game_tree.update(node, reward=1)

    best_play = game_tree.get_best_play(board.get_frozen(), depth=16)
    assert best_play == [
        (
            node,
            MonteCarloScore(
                times_visited=1,
                times_parent_visited=1,
                score=1,
                uct=DEFAULT_UCT,
            ),
        )
    ]


def test_get_best_play_depth_0(board, game_tree, parent_node, node):
    game_tree.update(parent_node, reward=1)
    game_tree.compute_score(node)
    game_tree.update(node, reward=1)

    best_play = game_tree.get_best_play(board.get_frozen(), depth=0)
    assert best_play == [
        (
            node,
            MonteCarloScore(
                times_visited=1,
                times_parent_visited=1,
                score=1,
                uct=DEFAULT_UCT,
            ),
        )
    ]


def test_get_best_play_depth_less(board, game_tree, parent_node, node):
    # stop at depth 0
    frozen = board.get_frozen()

    board.play(node.move_to_play)
    extra_node = Node(
        board=board.get_frozen(), move_to_play=Move(0, 3, Pawns.C, Colors.BLUE)
    )
    game_tree.add(extra_node)

    game_tree.compute_score(node)
    game_tree.compute_score(extra_node)

    game_tree.update(parent_node, reward=1)
    game_tree.update(node, reward=1)
    game_tree.update(extra_node, reward=1)

    best_play = game_tree.get_best_play(frozen, depth=0)
    assert best_play == [
        (
            node,
            MonteCarloScore(
                times_visited=1,
                times_parent_visited=1,
                score=1,
                uct=DEFAULT_UCT,
            ),
        )
    ]


def test_get_best_play_depth_1(board, game_tree, parent_node, node):
    # stop at depth 0
    frozen = board.get_frozen()
    board.play(node.move_to_play)
    extra_node = Node(
        board=board.get_frozen(), move_to_play=Move(0, 3, Pawns.C, Colors.BLUE)
    )
    game_tree.add(extra_node)

    game_tree.compute_score(node)
    game_tree.compute_score(extra_node)

    game_tree.update(parent_node, reward=1)
    game_tree.update(node, reward=1)
    game_tree.update(extra_node, reward=1)

    best_play = game_tree.get_best_play(frozen, depth=1)
    assert best_play == [
        (
            node,
            MonteCarloScore(
                times_visited=1,
                times_parent_visited=1,
                score=1,
                uct=DEFAULT_UCT,
            ),
        ),
        (
            extra_node,
            MonteCarloScore(
                times_visited=1,
                times_parent_visited=1,
                score=1,
                uct=DEFAULT_UCT,
            ),
        ),
    ]


# TODO test get_move_stats


def test_to_file(game_tree, tmp_path):
    game_tree.to_file(tmp_path, player_color=Colors.BLUE)


def test_from_file_red(game_tree, tmp_path, board):
    game_tree.to_file(tmp_path, player_color=Colors.RED)
    gm: GameTree = GameTree.from_file(
        tmp_path, depth=1, player_color=Colors.RED
    )
    assert gm._game_tree == {
        Node(
            board=board.get_frozen(),
            move_to_play=Move(2, 2, Pawns.A, Colors.RED),
        ): MonteCarloScore(
            times_visited=0, times_parent_visited=0, score=0, uct=DEFAULT_UCT
        ),
        Node(
            board=board.get_frozen(),
            move_to_play=Move(2, 3, Pawns.A, Colors.RED),
        ): MonteCarloScore(
            times_visited=0, times_parent_visited=0, score=0, uct=DEFAULT_UCT
        ),
    }
