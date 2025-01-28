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

    def add(self, node: Node):
        self._game_tree.setdefault(node, MonteCarloScore())

    def compute_score(self, node: Node, parent_node: Node | None):
        # TODO - game tree should be method agnostic ie no knowledge of montecarlo
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

    def get_best_move(self, frozen_board: FrozenBoard) -> Move | None:
        # TODO - game tree should be method agnostic ie no knowledge of montecarlo
        # Careful: if not all nodes have been visited, will ignore the unvisited nodes
        # Choose the most visited node
        best_move = None
        n_visited = None
        best_score = None
        for node, montecarlo in self._game_tree.items():
            if node.board == frozen_board and node.move_to_play is not None:
                if montecarlo.times_visited > 0:
                    if (
                        n_visited is None
                        or montecarlo.times_visited > n_visited
                        or (
                            montecarlo.times_visited == n_visited
                            and montecarlo.score > best_score
                        )
                    ):
                        best_move = node.move_to_play
                        n_visited = montecarlo.times_visited
                        best_score = montecarlo.score
        return best_move

    def get_best_play(self, frozen_board: FrozenBoard, depth: int = 16):
        best_node = None
        best_move = self.get_best_move(frozen_board)
        if best_move is None:
            # game tree scores have not been computed
            return list()
        best_node = Node(board=frozen_board, move_to_play=best_move)
        best_play = [(best_node, self._game_tree[best_node])]
        tmp_board = Board(board=frozen_board)

        for _ in range(depth):
            tmp_board.play(best_node.move_to_play)
            tmp_frozen_board = tmp_board.get_frozen()
            best_move = self.get_best_move(tmp_frozen_board)
            if best_move is None:
                break
            best_node = Node(board=tmp_frozen_board, move_to_play=best_move)
            best_play.append((best_node, self._game_tree[best_node]))
        return best_play

    def get_move_stats(self, frozen_board: FrozenBoard, depth: int = 16):
        best_play = self.get_best_play(
            frozen_board=frozen_board,
            depth=depth,
        )
        if len(best_play) == 0:
            return list()

        move_stats = [
            (node.move_to_play, montecarlo)
            for node, montecarlo in self._game_tree.items()
            if node.board == best_play[-1][0].board and node.move_to_play is not None
        ]
        move_stats.sort(key=lambda x: x[1].times_visited, reverse=True)
        return move_stats

    # TODO
    # Test, and remove these functions if I do not implement a pre-compute of the game tree
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
