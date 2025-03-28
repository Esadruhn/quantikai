import json
import pathlib

from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import MonteCarloScore
from quantikai.game import Board, Colors, FrozenBoard, Move
from quantikai.game.exceptions import InvalidFileException


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

    def compute_score(self, node: Node):
        return self._game_tree[node].compute_score()

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
            if node.board == best_play[-1][0].board
            and node.move_to_play is not None
        ]
        move_stats.sort(
            key=lambda x: (x[1].times_visited, x[1].score), reverse=True
        )
        return move_stats

    def get(self, depth: int) -> "GameTree":
        return GameTree(
            {
                node: montecarloscore
                for node, montecarloscore in self._game_tree.items()
                if len(node.board) == depth
            }
        )

    @staticmethod
    def sum(game_trees: list["GameTree"]) -> "GameTree":
        if len(game_trees) == 0:
            return GameTree()
        if len(game_trees) == 1:
            return game_trees[0]
        new_gm = dict()
        for node in game_trees[0]._game_tree:
            mscores = [
                g._game_tree[node] for g in game_trees if node in g._game_tree
            ]
            new_gm[node] = MonteCarloScore(
                times_visited=sum([m.times_visited for m in mscores]),
                times_parent_visited=sum(
                    [m.times_parent_visited for m in mscores]
                ),
                score=sum([m.score for m in mscores]),
                uct=sum([m.uct for m in mscores]),
            )
        return GameTree(new_gm)

    # TODO
    # Test, and remove these functions if I do not implement a pre-compute of the game tree
    def to_file(
        self, path: pathlib.Path, player_color: Colors, max_depth: int = 16
    ):
        # TODO - possible improvement: for each board keep only the best move
        # Not mandatory as the file size is < 500kB and it is nice for analysis purpose (eg board analysis function)
        if not path.is_dir():
            raise InvalidFileException(
                f"{path} does not exist or is not a directory."
            )

        for idx in range(max_depth):
            file_path = path / self.get_file_name(
                depth=idx, player_color=player_color
            )
            game_tree_json = [
                {
                    "node": node.to_compressed(),
                    "montecarlo": montecarlo.to_compressed(),
                }
                for node, montecarlo in self._game_tree.items()
                if len(node.board) == idx
                and node.move_to_play is not None
                and node.move_to_play.color == player_color
            ]
            if len(game_tree_json) > 0:
                file_path.write_text(json.dumps(game_tree_json))

    class GameTreeDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(
                self, object_hook=self.object_hook, *args, **kwargs
            )

        def object_hook(self, dct):
            if "node" in dct:
                return (
                    Node.from_compressed(dct["node"]),
                    MonteCarloScore.from_compressed(dct["montecarlo"]),
                )
            return dct

    @staticmethod
    def get_file_name(depth: int, player_color: Colors):
        return f"{depth}_{player_color.value}.json"

    @classmethod
    def from_file(
        cls, folder_path: pathlib.Path | None, depth: int, player_color: Colors
    ):
        if folder_path is None:
            raise InvalidFileException(
                f"The Montecarlo game tree file {folder_path} does not exist."
            )
        file_path = pathlib.Path(folder_path) / cls.get_file_name(
            depth=depth, player_color=player_color
        )
        if not file_path.exists():
            raise InvalidFileException(
                f"The Montecarlo game tree file {file_path} does not exist."
            )
        game_tree_as_list = json.loads(
            file_path.read_text(), cls=cls.GameTreeDecoder
        )
        game_tree: dict[Node, MonteCarloScore] = {
            n: m for n, m in game_tree_as_list
        }
        return cls(game_tree)
