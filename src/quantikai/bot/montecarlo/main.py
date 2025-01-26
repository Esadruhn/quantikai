import copy
from dataclasses import asdict
import pathlib
import json

from quantikai.game import Board, FrozenBoard, Player, Move
from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import MonteCarloScore
from quantikai.bot.montecarlo.game_tree import GameTree

ITERATIONS = 5000
USE_DEPTH = True


def _explore_node(
    game_tree: GameTree,
    parent_node: Node,
    board: Board,
    player: Player,
) -> tuple[bool, Node | None]:
    """Explore one node: compute children nodes and execute one.

    Returns:
        - game is over
        - it is a win for the current player
        - explored node (None if there is no possible move)
    Updates:
        - player
        - board
        - game tree (computed the scores of the possible next nodes)
    """
    possible_moves = board.get_possible_moves(
        player.pawns,
        player.color,
        optimize=True,
    )

    # end case: the parent node is a leaf node
    if len(possible_moves) == 0:
        return True, None

    # Choose the node with the best trade-off exploration/exploitation
    node_to_explore = None
    uct = None
    for pos_mov in possible_moves:
        node = Node(board=board.get_frozen(), move_to_play=pos_mov)
        new_uct = game_tree.add(
            node=node,
            parent_node=parent_node,
        )
        if uct is None or new_uct >= uct:
            node_to_explore = node
            uct = new_uct

    # Play the chosen move and evaluate: leaf node or keep going
    is_win = board.play(node_to_explore.move_to_play)
    player.remove(node_to_explore.move_to_play.pawn)

    return is_win, node_to_explore


def _montecarlo_algo(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int,
    use_depth: bool,
) -> GameTree:
    """Execute the montecarlo algorithm, up to generating
    the 'game tree' i.e. the graph of the moves with their
    scores.
    """
    frozen_board = board.get_frozen()  # hashable version of the board
    root_node = Node(board=frozen_board)
    game_tree = GameTree()
    game_tree.add(node=root_node, parent_node=None)

    for _ in range(iterations):
        is_current = False  # which player is playing

        parent_node = root_node

        tmp_board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)
        tmp_other = copy.deepcopy(other_player)

        # We keep a list of the nodes we explore at each iteration
        # so that at the end we can backtrack the scores and UCT evaluation
        iteration_nodes = list([root_node])
        # The reward is higher if the game ends sooner
        depth_reward = 16
        node_to_explore = None

        while 1:
            is_current = not is_current
            player = tmp_player if is_current else tmp_other
            game_is_over, node_to_explore = _explore_node(
                game_tree=game_tree,
                parent_node=parent_node,
                board=tmp_board,
                player=player,
            )
            if node_to_explore is not None:
                iteration_nodes.append(node_to_explore)
            if game_is_over:
                break
            depth_reward -= 1
            # TODO: check this, I added it, bug before !!!
            parent_node = node_to_explore

        # Backtrack the scores and iterations
        reward = None
        if node_to_explore is None:
            # current_player loses
            reward = 0
        else:
            # current_player wins
            reward = 1
        if use_depth:
            reward = reward * use_depth

        while len(iteration_nodes) > 0:
            node = iteration_nodes.pop()
            game_tree.update(node=node, reward=reward)
            is_current = not is_current
            if reward == 0:
                reward = 1
                if use_depth:
                    reward = use_depth
            else:
                reward = 0
    return game_tree


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    game_tree_file: pathlib.Path | None = None,
) -> tuple[float, Move]:
    """http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf
    Upper Confidence Bounds for Trees (UCT)

    There is a statitical way of defining the best number of iterations:
    see https://kb.palisade.com/index.php?pg=kb.page&id=125
    use_depth is meant to reduce the necessary number of iterations and encourage visiting paths
    that lead to a quick win.

    Test the "iterations" variable: run the algo on an empty board and look at the "best" play i.e. the path
    of most visited nodes, see after which depth the nodes have been visited only once.
    e.g. here we see that with 5000 iterations, depth = 4
    [{"color":"BLUE","pawn":"A","x":2,"y":2},{"score":9404,"times_visited":897,"uct":10.676760650853348}]
    [{"color":"RED","pawn":"D","x":3,"y":0},{"score":2168,"times_visited":353,"uct":6.444225713864206}]
    [{"color":"BLUE","pawn":"C","x":3,"y":3},{"score":834,"times_visited":78,"uct":11.346311423620698}]
    [{"color":"RED","pawn":"C","x":0,"y":1},{"score":67,"times_visited":12,"uct":7.250682783483356}]
    [{"color":"BLUE","pawn":"A","x":1,"y":3},{"score":12,"times_visited":1,"uct":10000}]

    With use_depth=True:
    - 1000 iterations - 3
    - 5000 iterations - 4

    With use_depth=False:
    TODO

    Args:
        board (Board): _description_
        current_player (Player): _description_
        other_player (Player): _description_
        iterations (int, optional): _description_. Defaults to 500.
        use_depth (bool, optional): Victory score is better if fewer moves are needed (between 16 and 1). Defaults to True

    Returns:
        tuple[float, Move]: _description_
    """
    frozen_board = board.get_frozen()  # hashable version of the board
    game_tree = None
    if game_tree_file is not None:
        game_tree = GameTree.from_file(path=game_tree_file)
    else:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
        )

    return game_tree.get_best_move(frozen_board)


def _get_best_play_from_game_tree(
    frozen_board: FrozenBoard,
    game_tree: dict[Node, MonteCarloScore],
    depth: int,
) -> list[tuple[Node, MonteCarloScore]]:
    best_node = None
    best_montecarlo = None
    for node, montecarlo in game_tree.items():
        if (
            node.board == frozen_board
            and node.move_to_play is not None
            and (
                best_montecarlo is None
                or montecarlo.times_visited > best_montecarlo.times_visited
            )
        ):
            best_node = node
            best_montecarlo = montecarlo
    if best_node is None:
        return list()

    best_play = [(best_node, best_montecarlo)]
    tmp_board = Board(board=frozen_board.board)

    idx = 0
    while 1:
        if idx >= depth:
            break

        tmp_board.play(best_node.move_to_play)
        tmp_frozen_board = tmp_board.get_frozen()
        best_node = None
        best_montecarlo = None
        for node, montecarlo in game_tree.items():
            if node.board == tmp_frozen_board and (
                best_montecarlo is None
                or montecarlo.times_visited > best_montecarlo.times_visited
            ):
                best_node = node
                best_montecarlo = montecarlo

        if best_node is None:
            break
        best_play.append((best_node, best_montecarlo))
        idx += 1
    return best_play


class GameTreeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

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


def _load_game_tree_from_file(game_tree_file):
    game_tree_as_list = json.loads(
        pathlib.Path(game_tree_file).read_text(), cls=GameTreeDecoder
    )
    game_tree: dict[Node, MonteCarloScore] = {n: m for n, m in game_tree_as_list}
    return game_tree


def get_move_stats(
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 0,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    game_tree_file: pathlib.Path | None = None,
) -> list[tuple[Move, MonteCarloScore]]:
    frozen_board = board.get_frozen()  # hashable version of the board
    game_tree = None
    if game_tree_file is not None:
        game_tree = _load_game_tree_from_file(game_tree_file)
    else:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
        )
    best_play = _get_best_play_from_game_tree(
        frozen_board=frozen_board,
        game_tree=game_tree,
        depth=depth,
    )
    if len(best_play) == 0:
        return list()

    move_stats = [
        (node.move_to_play, montecarlo)
        for node, montecarlo in game_tree.items()
        if node.board == best_play[-1][0].board and node.move_to_play is not None
    ]
    move_stats.sort(key=lambda x: x[1].times_visited, reverse=True)
    return move_stats


def get_best_play(
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 16,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    game_tree_file: pathlib.Path | None = None,
) -> list[tuple[Node, MonteCarloScore]]:

    frozen_board = board.get_frozen()  # hashable version of the board
    game_tree = None
    if game_tree_file is not None:
        game_tree = _load_game_tree_from_file(game_tree_file)
    else:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
        )

    return _get_best_play_from_game_tree(
        frozen_board=frozen_board, game_tree=game_tree, depth=depth
    )


def generate_tree(
    path: pathlib.Path,
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
):

    game_tree = _montecarlo_algo(
        board=board,
        current_player=current_player,
        other_player=other_player,
        iterations=iterations,
        use_depth=use_depth,
    )
    # game_tree to json
    game_tree_json = (
        {
            "node": node.to_json(),
            "montecarlo": asdict(montecarlo),
        }
        for node, montecarlo in game_tree.items()
    )

    class StreamArray(list):
        def __iter__(self):
            return game_tree_json

        def __len__(self):
            return 1

    pathlib.Path(path).write_text(json.dumps(StreamArray()))
