import itertools

from quantikai import bot, game


class InvalidInputError(Exception):
    def __init__(self, message):
        super().__init__(message)


def parse_input(user_input: str):
    inp = user_input.strip().split()
    if len(inp) != 3:
        raise InvalidInputError(
            "Wrong number of arguments, please enter 'x y pawn_name'"
        )
    try:
        int(inp[0])
        int(inp[1])
    except ValueError:
        raise InvalidInputError(
            "Please enter the coordinates of your pawn as"
            "numbers separated by a space, e.g. 0 1 "
        )
    try:
        game.Pawns[inp[2]]
    except:
        raise InvalidInputError(
            "Valid values for the pawn are: "
            + str([x.name for x in game.Pawns])
        )
    return int(inp[0]), int(inp[1]), game.Pawns[inp[2]]


def init_game():
    board = game.Board()
    players = [
        game.Player(color=game.Colors.BLUE),
        game.Player(color=game.Colors.RED),
    ]

    player_cycle = itertools.cycle(players)
    return board, player_cycle


def _human_player_loop(board, player):
    pawn_list = player.get_printable_list_pawns()
    x, y, pawn = None, None, None
    while 1:
        user_input = input(
            "Player "
            + player.color.name
            + ", please play ("
            + pawn_list
            + ")\n"
        )
        try:
            x, y, pawn = parse_input(user_input)
            break
        except InvalidInputError as e:
            print(e)

    player.check_has_pawn(pawn)
    is_a_win = board.play(game.Move(x, y, pawn, player.color))
    player.remove(pawn)
    board.print()
    return is_a_win


def human_play():
    """Two humans play Quantik"""
    # Init the game elements
    board, player_cycle = init_game()
    player = next(player_cycle)

    print("Welcome to the Quantik game!")
    print("Example of a valid first move: 0 0 A\n")

    while 1:
        try:
            is_a_win = _human_player_loop(board, player)
            if is_a_win:
                print(
                    "Congratulations, player " + player.color.name + " WINS !"
                )
                break
        except game.InvalidMoveError as e:
            print(e)
            continue
        player = next(player_cycle)
        if not board.have_possible_move(player.color):
            print(
                "Player "
                + player.color.name
                + " has no possible move left, he loses!"
            )
            break


def bot_play():
    """Play against a bot"""
    board, player_cycle = init_game()
    player = next(player_cycle)

    print("Welcome to the Quantik game!")
    print("Example of a valid first move: 0 0 A\n")

    user_input = input("Do you want to start (\033[1myes\033[0m/no)? ")
    answer = user_input.strip() == "" or user_input.strip() == "yes"
    if not answer:
        player = next(player_cycle)

    while 1:
        try:
            if not board.have_possible_move(player.color):
                print(
                    "Player "
                    + player.color.name
                    + " has no possible move left, he loses!"
                )
                break

            is_a_win = False
            if player.color == game.Colors.BLUE:
                # Human player's turn
                is_a_win = _human_player_loop(board, player)
            else:
                # Bot's turn
                other_player = next(player_cycle)
                next(player_cycle)  # Compensate

                move = bot.get_best_move(board, player, other_player)
                if move is None:
                    print(
                        "Player " + player.color.name + " gives up and loses."
                    )
                    break
                is_a_win = board.play(move)
                player.remove(move.pawn)
                board.print()

            if is_a_win:
                print(
                    "Congratulations, player " + player.color.name + " WINS !"
                )
                break
        except game.InvalidMoveError as e:
            print(e)
            continue
        player = next(player_cycle)
