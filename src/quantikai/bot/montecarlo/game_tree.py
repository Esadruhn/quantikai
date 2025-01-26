import pathlib
import json

from dataclasses import asdict

from quantikai.game import Board, FrozenBoard, Move
from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import MonteCarloScore


class GameTreeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class GameTree:
    _game_tree: dict[Node, MonteCarloScore]

    def __init__(self, game_tree=None):
        self._game_tree = dict()
        if game_tree is not None:
            self._game_tree = game_tree

    def add(self, node: Node, parent_node: Node | None):
        # TODO - game tree should be method agnostic ie no knowledge of montecarlo
        self._game_tree.setdefault(node, MonteCarloScore())
        times_visited = 0
        # two possibilities: root node has None for parent node
        # and parent_node is not in game tree because this is a graph, not a tree
        if parent_node in self._game_tree:
            times_visited = self._game_tree[parent_node].times_visited
        return self._game_tree[node].compute_score(
            times_parent_visited=times_visited,
        )

    def update(self, node: Node, reward: int):
        self._game_tree[node].times_visited += 1
        self._game_tree[node].score += reward

    def get_best_move(
        self, frozen_board: FrozenBoard
    ) -> tuple[float | None, Move | None]:
        # TODO - game tree should be method agnostic ie no knowledge of montecarlo
        # Choose the most visited node
        best_move = None
        n_visited = None
        winning_avg = None
        for node, montecarlo in self._game_tree.items():
            if node.board == frozen_board and node.move_to_play is not None:
                # This will trigger if nb of iterations < nb of possible moves
                assert montecarlo.times_visited > 0, "The node has never been visited."
                if n_visited is None or montecarlo.times_visited > n_visited:
                    best_move = node.move_to_play
                    n_visited = montecarlo.times_visited
                    winning_avg = montecarlo.score / montecarlo.times_visited
        return (winning_avg, best_move)

    def to_file(self, path: pathlib.Path):
        game_tree_json = (
            {
                "node": node.to_json(),
                "montecarlo": asdict(montecarlo),
            }
            for node, montecarlo in self._game_tree.items()
        )

        class StreamArray(list):
            def __iter__(self):
                return game_tree_json

            def __len__(self):
                return 1

        pathlib.Path(path).write_text(json.dumps(StreamArray()))

    class GameTreeDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(
                self, object_hook=self.object_hook, *args, **kwargs
            )

        def object_hook(self, dct):
            if "node" in dct:
                return (
                    Node(
                        board=tuple(
                            tuple(None if item is None else tuple(item) for item in row)
                            for row in dct["node"]["board"]
                        ),
                        move_to_play=(
                            None
                            if dct["node"]["move_to_play"] is None
                            else Move(**dct["node"]["move_to_play"])
                        ),
                    ),
                    MonteCarloScore(**dct["montecarlo"]),
                )
            return dct

    @classmethod
    def from_file(cls, path: pathlib.Path):
        game_tree_as_list = json.loads(
            pathlib.Path(path).read_text(), cls=cls.GameTreeDecoder
        )
        game_tree: dict[Node, MonteCarloScore] = {n: m for n, m in game_tree_as_list}
        return cls(game_tree)
