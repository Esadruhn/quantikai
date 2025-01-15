import copy
import math
from dataclasses import dataclass

from quantikai.game_elements import Board, FrozenBoard, Player, Pawns, Colors

# MonteCarlo variable - 1/sqrt(2)
UCT_CST = 0.7


@dataclass(frozen=True, eq=True)
class Node:
    """Hashable class to represent a node in a tree representation of the game.
    A node is a state of the board and a parent_move to apply to the board.
    For the initial state of the game parent_move is None.
    """

    board: FrozenBoard
    parent_move: tuple[int, int, Pawns, Colors] = None


@dataclass
class MonteCarloScore:
    """Compute values for each node
    for the Monte-Carlo UCT algorithm.
    """

    times_visited: int = 0  # Number of times the nodes has been visited
    score: int = 0  # Sum of the iteration rewards
    uct: int = 10000  # UCT value, that represents a trade-off exploration/exploitation


def _montecarlo_uct(score: int, times_visited: int, times_parent_visited: int) -> float:
    if times_visited == 0:
        return 10000
    return (score / times_visited) + 2 * UCT_CST * math.sqrt(
        2 * math.log(times_parent_visited) / times_visited
    )


def montecarlo(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = 1000,
) -> tuple[int, tuple[int, int, Pawns, Colors]]:
    """http://www.incompleteideas.net/609%20dropbox/other%20readings%20and%20resources/MCTS-survey.pdf
    Upper Confidence Bounds for Trees (UCT)

    Args:
        board (Board): _description_
        current_player (Player): _description_
        other_player (Player): _description_
        iterations (int, optional): _description_. Defaults to 500.

    Returns:
        tuple[int, tuple[int, int, Pawns, Colors]]: _description_
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
        iteration_score = 0

        while 1:
            is_current = not is_current
            player = tmp_player if is_current else tmp_other
            possible_moves = tmp_board.get_possible_moves(
                player.pawns,
                player.color,
                optimize=True,
            )

            # end case: the parent node is a leaf node
            if len(possible_moves) == 0:
                if not is_current:
                    iteration_score = 1
                break

            # Choose the node with the best trade-off exploration/exploitation
            node_to_explore = None
            uct = None
            for pos_mov in possible_moves:
                node = Node(board=tmp_board.get_frozen(), parent_move=pos_mov)
                game_tree.setdefault(node, MonteCarloScore())
                game_tree[node].uct = _montecarlo_uct(
                    score=game_tree[node].score,
                    times_visited=game_tree[node].times_visited,
                    times_parent_visited=game_tree[parent_node].times_visited,
                )
                if uct is None or game_tree[node].uct >= uct:
                    node_to_explore = node
                    uct = game_tree[node].uct

            # Play the chosen move and evaluate: leaf node or keep going
            is_win = tmp_board.play(*node_to_explore.parent_move)
            player.remove(node_to_explore.parent_move[2])
            # TODO check the update of the leaf nodes
            iteration_nodes.append(node_to_explore)

            if is_win:
                if is_current:
                    iteration_score = 1
                break

        # Backtrack the scores and iterations
        while len(iteration_nodes) > 0:
            node = iteration_nodes.pop()
            game_tree[node].times_visited += 1
            game_tree[node].score += iteration_score

    # Choose the most visited node
    best_move = None
    n_visited = None
    winning_avg = None

    for node, montecarlo in game_tree.items():
        if node.board == frozen_board and node.parent_move is not None:
            if n_visited is None or montecarlo.times_visited > n_visited:
                best_move = node.parent_move
                n_visited = montecarlo.times_visited
                winning_avg = montecarlo.score / montecarlo.times_visited
    if winning_avg is not None:
        if winning_avg < 0.5:
            print("I don't like this move")
        elif winning_avg > 0.9:
            print("I am going to win, oh yeah")
    return (winning_avg, best_move)


def minmax(
    player_max: Colors,
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 0,
) -> tuple[int, tuple[int, int, Pawns, Colors]]:

    possible_moves = board.get_possible_moves(
        current_player.pawns,
        current_player.color,
        optimize=True,
    )
    if len(possible_moves) == 0:
        if current_player.color == player_max:
            return -1, None
        return 1, None

    best_move = None
    best_score = None
    # If no winning move in sight, we try to drag the game
    # so that the opponent may make a mistake
    # TODO: test
    best_depth = None
    for move in possible_moves:
        tmp_board = copy.deepcopy(board)
        tmp_player = copy.deepcopy(current_player)
        is_a_win = tmp_board.play(*move)
        tmp_player.remove(move[2])

        move_score = None
        if is_a_win and tmp_player.color == player_max:
            move_score = 1
        if is_a_win and tmp_player.color != player_max:
            move_score = -1
        if not is_a_win:
            move_score, _ = minmax(
                player_max=player_max,
                board=tmp_board,
                current_player=other_player,
                other_player=tmp_player,
                depth=depth + 1,
            )

        if tmp_player.color == player_max:
            # Maximise the score
            if best_score is None or best_score < move_score:
                best_move = move
                best_score = move_score
                best_depth = depth
                # break and do not evaluate other moves if is max
                if best_score == 1:
                    break
            elif best_score == move_score and depth > best_depth:
                best_move = move
                best_depth = depth
        else:
            # Minimize the score
            if best_score is None or best_score > move_score:
                best_move = move
                best_score = move_score
                best_depth = depth
                # break and do not evaluate other moves if is min
                if best_score == -1:
                    break
            elif best_score == move_score and depth > best_depth:
                best_move = move
                best_depth = depth
    return (best_score, best_move)


def get_best_move(
    board: Board, current_player: Player, other_player: Player
) -> tuple[int, int, Pawns]:

    # TODO - decide between strategies
    if True:
        best_score, best_move = montecarlo(
            board=board,
            current_player=current_player,
            other_player=other_player,
        )
    else:
        best_score, best_move = minmax(
            player_max=current_player.color,
            board=board,
            current_player=current_player,
            other_player=other_player,
        )
        if best_score != 1:
            # because sass is the game
            print("If you play optimally you will win.")
    return best_move
