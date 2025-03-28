import copy
import multiprocessing
import pathlib
import random

from quantikai.bot.montecarlo.game_tree import GameTree
from quantikai.bot.montecarlo.node import Node
from quantikai.bot.montecarlo.score import MonteCarloScore
from quantikai.game import Board, Colors, Move, Player
from quantikai.game.exceptions import InvalidFileException

ITERATIONS = 10000
USE_DEPTH = True
GAME_TREE_FILE_MAX_DEPTH = 2
NUM_PROCESS = 1


def _explore_node(
    game_tree: GameTree,
    board: Board,
    player: Player,
    all_possible_moves: bool,
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
        optimize=not all_possible_moves,
    )
    # Order the possible moves randomly for the single-run parallelization
    possible_moves = list(possible_moves)
    random.shuffle(possible_moves)

    # Choose the node with the best trade-off exploration/exploitation
    node_to_explore = None
    uct = None
    frozen_board = board.get_frozen()
    for pos_mov in possible_moves:
        node = Node(board=frozen_board, move_to_play=pos_mov)
        game_tree.add(node)
        new_uct = game_tree.compute_score(node=node)
        if uct is None or new_uct >= uct:
            node_to_explore = node
            uct = new_uct

    if node_to_explore is None:
        # it means that len(possible_moves) == 0
        # end case: the parent node is a leaf node
        return True, None

    # Play the chosen move and evaluate: leaf node or keep going
    is_win = board.play(node_to_explore.move_to_play, strict=False)
    player.remove(node_to_explore.move_to_play.pawn)

    return is_win, node_to_explore


def _one_process_algo(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int,
    use_depth: bool,
    all_possible_moves: bool = False,
    multiprocess_list: list = None,
) -> GameTree:

    frozen_board = board.get_frozen()  # hashable version of the board
    root_node = Node(board=frozen_board)
    game_tree = GameTree()
    game_tree.add(node=root_node)

    random.seed()

    for _ in range(iterations):
        is_current = False  # which player is playing

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
                board=tmp_board,
                player=player,
                all_possible_moves=all_possible_moves,
            )
            if node_to_explore is not None:
                iteration_nodes.append(node_to_explore)
            if game_is_over:
                break
            depth_reward -= 1

        # Backtrack the scores and iterations
        reward = None
        if node_to_explore is None:
            # current_player loses
            reward = 0
        else:
            # current_player wins
            reward = 1
        if use_depth:
            reward = reward * depth_reward

        while len(iteration_nodes) > 0:
            node = iteration_nodes.pop()
            game_tree.update(node=node, reward=reward)
            is_current = not is_current
            if reward == 0:
                reward = 1
                if use_depth:
                    reward = depth_reward
            else:
                reward = 0
    if multiprocess_list is not None:
        multiprocess_list.append(game_tree.get(depth=len(frozen_board)))
    return game_tree


def _montecarlo_algo(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int,
    use_depth: bool,
    all_possible_moves: bool = False,
    num_process: int = NUM_PROCESS,
) -> GameTree:
    """Execute the montecarlo algorithm, up to generating the 'game tree' i.e. the graph of the moves with their scores.
    Args:
        board (Board): _description_
        current_player (Player): _description_
        other_player (Player): _description_
        iterations (int): _description_
        use_depth (bool): _description_
        all_possible_moves (bool, optional): whether to consider redundant moves or not (eg by exploiting board symmetry). Defaults to False.

    Returns:
        GameTree: _description_
    """
    if num_process == 1:
        return _one_process_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
            all_possible_moves=all_possible_moves,
        )
    manager = multiprocessing.Manager()
    multiprocess_list = manager.list()
    jobs = list()
    for _ in range(num_process):
        p = multiprocessing.Process(
            target=_one_process_algo,
            args=(
                board,
                current_player,
                other_player,
                iterations,
                use_depth,
                all_possible_moves,
                multiprocess_list,
            ),
        )
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    return GameTree.sum(list(multiprocess_list))


def get_best_move(
    board: Board,
    current_player: Player,
    other_player: Player,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    num_process=NUM_PROCESS,
    game_tree_folder: pathlib.Path | None = None,
) -> Move | None:
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
    try:
        game_tree = GameTree.from_file(
            folder_path=game_tree_folder,
            depth=len(frozen_board),
            player_color=current_player.color,
        )
    except InvalidFileException:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
            num_process=num_process,
        )

    return game_tree.get_best_move(frozen_board)


def get_move_stats(
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 0,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    num_process: int = NUM_PROCESS,
    game_tree_folder: pathlib.Path | None = None,
) -> list[tuple[Move, MonteCarloScore]]:
    frozen_board = board.get_frozen()  # hashable version of the board
    game_tree = None
    try:
        game_tree = GameTree.from_file(
            folder_path=game_tree_folder,
            depth=len(frozen_board),
            player_color=current_player.color,
        )
    except InvalidFileException:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
            num_process=num_process,
        )
    return game_tree.get_move_stats(frozen_board=frozen_board, depth=depth)


def get_best_play(
    board: Board,
    current_player: Player,
    other_player: Player,
    depth: int = 16,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    num_process: int = NUM_PROCESS,
    game_tree_folder: pathlib.Path | None = None,
) -> list[tuple[Node, MonteCarloScore]]:

    frozen_board = board.get_frozen()  # hashable version of the board
    game_tree = None
    try:
        game_tree = GameTree.from_file(
            folder_path=game_tree_folder,
            depth=len(frozen_board),
            player_color=current_player.color,
        )
    except InvalidFileException:
        game_tree = _montecarlo_algo(
            board=board,
            current_player=current_player,
            other_player=other_player,
            iterations=iterations,
            use_depth=use_depth,
            num_process=num_process,
        )
    return game_tree.get_best_play(
        frozen_board=frozen_board,
        depth=depth,
    )


def generate_tree(
    path: pathlib.Path,
    board: Board,
    first_player: Player,
    second_player: Player,
    main_player_color: Colors,
    max_depth: int = GAME_TREE_FILE_MAX_DEPTH,
    iterations: int = ITERATIONS,
    use_depth: bool = USE_DEPTH,
    num_process=NUM_PROCESS,
) -> None:
    """Generate the MonteCarlo algorithm game tree and
    save it to a file.

    Args:
        path (pathlib.Path): path where to save the generated file
        board (Board): starting board
        first_player (Player): player that plays first on this board
        second_player (Player): player that plays second on this board
        main_player_color (Colors): keep only the moves for that player
        max_depth (int, optional): max depth of the game tree that is saved. Defaults to GAME_TREE_FILE_MAX_DEPTH.
        iterations (int, optional): MonteCarlo algorithm parameter: number of iterations. Defaults to ITERATIONS.
        use_depth (bool, optional): MonteCarlo algorithm parameter: reward depends on the depth. Defaults to USE_DEPTH.
    """
    # whether we use all possible moves or remove the redundant ones
    all_possible_moves = not (
        max_depth <= 2 and main_player_color == first_player.color
    )
    game_tree = _montecarlo_algo(
        board=board,
        current_player=first_player,
        other_player=second_player,
        iterations=iterations,
        use_depth=use_depth,
        all_possible_moves=all_possible_moves,
        num_process=num_process,
    )
    game_tree.to_file(
        path=path, player_color=main_player_color, max_depth=max_depth
    )
