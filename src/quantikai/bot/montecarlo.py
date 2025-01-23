import copy
import math
from dataclasses import dataclass
import random

from quantikai.game import Board, FrozenBoard, Player, Pawns, Colors, Move

DEFAULT_UCT = 10000 # + infinite

@dataclass(frozen=True, eq=True)
class Node:
    """Hashable class to represent a node in a tree representation of the game.
    A node is a state of the board and a parent_move to apply to the board.
    For the initial state of the game parent_move is None.
    """

    board: FrozenBoard
    parent_move: Move = None


@dataclass
class MonteCarloScore:
    """Compute values for each node
    for the Monte-Carlo UCT algorithm.
    """

    times_visited: int = 0  # Number of times the nodes has been visited
    score: int = 0  # Sum of the iteration rewards
    uct: int = DEFAULT_UCT  # UCT value, that represents a trade-off exploration/exploitation


def _montecarlo_uct(
    score: int, times_visited: int, times_parent_visited: int, uct_cst: float
) -> float:
    if times_visited == 0:
        return DEFAULT_UCT
    return (score / times_visited) + 2 * uct_cst * math.sqrt(
        2 * math.log(times_parent_visited) / times_visited
    )


def _explore_node(
    game_tree: set[Node, MonteCarloScore],
    parent_node: Node,
    is_current: bool,
    board: Board,
    player: Player,
    uct_cst: float,
) -> tuple[int, Node, Player, Board, set[Node, MonteCarloScore]]:
    """Explore one node: compute children nodes and execute one"""

    iteration_score = 0

    possible_moves = board.get_possible_moves(
        player.pawns,
        player.color,
        optimize=True,
    )

    # end case: the parent node is a leaf node
    if len(possible_moves) == 0:
        if not is_current:
            iteration_score = 1
        return iteration_score, None, player, board, game_tree

    # Choose the node with the best trade-off exploration/exploitation
    node_to_explore = None
    uct = None
    for pos_mov in possible_moves:
        node = Node(board=board.get_frozen(), parent_move=pos_mov)
        game_tree.setdefault(node, MonteCarloScore())
        game_tree[node].uct = _montecarlo_uct(
            score=game_tree[node].score,
            times_visited=game_tree[node].times_visited,
            times_parent_visited=game_tree[parent_node].times_visited,
            uct_cst=uct_cst,
        )
        if uct is None or game_tree[node].uct >= uct:
            node_to_explore = node
            uct = game_tree[node].uct

    # Play the chosen move and evaluate: leaf node or keep going
    is_win = board.play(node_to_explore.parent_move)
    player.remove(node_to_explore.parent_move.pawn)

    if is_win:
        iteration_score = 1
        return 1, node_to_explore, player, board, game_tree

    return None, node_to_explore, player, board, game_tree


def _montecarlo_algo(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int,
    uct_cst: float,
    use_depth: bool,
) -> dict[Node, MonteCarloScore]:
    """Execute the montecarlo algorithm, up to generating
    the 'game tree' i.e. the graph of the moves with their
    scores.
    """
    frozen_board = board.get_frozen()  # hashable version of the board
    root_node = Node(board=frozen_board)
    game_tree = {root_node: MonteCarloScore()}
    # TODO? save game tree for further iterations in one game? some must overlap

    for _ in range(iterations):
        is_current = False  # which player is playing

        parent_node = root_node

        tmp_board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)
        tmp_other = copy.deepcopy(other_player)

        # We keep a list of the nodes we explore at each iteration
        # so that at the end we can backtrack the scores and UCT evaluation
        iteration_nodes = list([root_node])
        depth = 16

        while 1:
            is_current = not is_current
            player = tmp_player if is_current else tmp_other
            iteration_score, node_to_explore, player, tmp_board, game_tree = (
                _explore_node(
                    game_tree=game_tree,
                    parent_node=parent_node,
                    is_current=is_current,
                    board=tmp_board,
                    player=player,
                    uct_cst=uct_cst,
                )
            )
            if node_to_explore is not None:
                iteration_nodes.append(node_to_explore)
            if iteration_score is not None:
                if use_depth:
                    iteration_score = depth
                break

            depth -= 1

        # Backtrack the scores and iterations
        while len(iteration_nodes) > 0:
            node = iteration_nodes.pop()
            game_tree[node].times_visited += 1
            adjustable = 16 if use_depth else 1
            if is_current:
                game_tree[node].score += iteration_score
            else:
                game_tree[node].score += adjustable - iteration_score
            is_current = not is_current
    return game_tree


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = 1000,
    uct_cst: float = 0.7,
    use_depth: bool = True,
) -> tuple[int, tuple[int, int, Pawns, Colors]]:
    """http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf
    Upper Confidence Bounds for Trees (UCT)

    There is a statitical way of defining the best number of iterations:
    see https://kb.palisade.com/index.php?pg=kb.page&id=125
    With use_depth, doe snot need may iterations (100). Without it, the algorithm easily
    misses an instant win if there are many possible moves to investigate, even with 10'000
    iterations.

    Args:
        board (Board): _description_
        current_player (Player): _description_
        other_player (Player): _description_
        iterations (int, optional): _description_. Defaults to 500.
        uct_cst (float, optional): 0.7 (1/sqrt(2) works well
        use_depth (bool, optional): Victory score is better if fewer moves are needed (between 16 and 1). Defaults to True

    Returns:
        tuple[int, tuple[int, int, Pawns, Colors]]: _description_
    """
    frozen_board = board.get_frozen()  # hashable version of the board

    game_tree = _montecarlo_algo(
        board=board,
        current_player=current_player,
        other_player=other_player,
        iterations=iterations,
        uct_cst=uct_cst,
        use_depth=use_depth,
    )

    # Choose the most visited node
    best_move = None
    n_visited = None
    winning_avg = None

    for node, montecarlo in game_tree.items():
        if node.board == frozen_board and node.parent_move is not None:
            # This should never trigger unless nb of iterations < nb of possible moves
            assert montecarlo.times_visited > 0, "The node has never been visited."
            if n_visited is None or montecarlo.times_visited > n_visited:
                best_move = node.parent_move
                n_visited = montecarlo.times_visited
                winning_avg = montecarlo.score / montecarlo.times_visited
    return (winning_avg, best_move)


def get_move_stats(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = 1000,
    uct_cst: float = 0.7,
    use_depth: bool = True,
) -> list[tuple[Move, MonteCarloScore]]:
    frozen_board = board.get_frozen()  # hashable version of the board

    game_tree = _montecarlo_algo(
        board=board,
        current_player=current_player,
        other_player=other_player,
        iterations=iterations,
        uct_cst=uct_cst,
        use_depth=use_depth,
    )

    return [
        (node.parent_move, montecarlo)
        for node, montecarlo in game_tree.items()
        if node.board == frozen_board and node.parent_move is not None
    ].sort(key=lambda x: x[1].times_visited)

def get_best_play(board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = 1000,
    uct_cst: float = 0.7,
    use_depth: bool = True,
) -> list[tuple[Move, MonteCarloScore]]:

    frozen_board = board.get_frozen()  # hashable version of the board

    game_tree = _montecarlo_algo(
        board=board,
        current_player=current_player,
        other_player=other_player,
        iterations=iterations,
        uct_cst=uct_cst,
        use_depth=use_depth,
    )

    best_play = list()
    next_moves = [(node.parent_move, montecarlo)
        for node, montecarlo in game_tree.items()
        if node.board == frozen_board and node.parent_move is not None
    ]
    if len(next_moves) == 0:
        return []
    move = max(next_moves, key=lambda x: x[1].times_visited)
    best_play.append(move)
    tmp_board = copy.deepcopy(board)
    while(1):
        tmp_board.play(move)
        next_moves = [(node.parent_move, montecarlo) for node, montecarlo in game_tree.items() if node.board == tmp_board.get_frozen()]
        if len(next_moves) == 0:
            break
        move = max(next_moves, key=lambda x: x[1].times_visited)
        best_play.append(move)
    return best_play


