"""Console script for game_elements."""
import typer
from rich.console import Console
import itertools
import random

from quantikai import game_elements, minmax

app = typer.Typer()
console = Console()

class InvalidInputError(Exception):
    def __init__(self, message):
        super().__init__(message)

def parse_input(user_input: str):
    inp = user_input.strip().split()
    if len(inp) != 3: raise InvalidInputError("Wrong number of arguments, please enter 'x y pawn_name'")
    try:
        int(inp[0])
        int(inp[1])
    except ValueError:
        raise InvalidInputError("Please enter the coordinates of your pawn as numbers separated by a space, e.g. 0 1 ")
    try:
        game_elements.Pawns[inp[2]]
    except:
        raise InvalidInputError("Valid values for the pawn are: " + str([x.name for x in game_elements.Pawns]))
    return int(inp[0]), int(inp[1]), game_elements.Pawns[inp[2]]

def init_game():
    board = game_elements.Board()
    players = [game_elements.Player(color=game_elements.Colors.BLUE),game_elements.Player(color=game_elements.Colors.RED)]

    player_cycle = itertools.cycle(players)
    return board, player_cycle

def human_player_loop(board, player):
    pawn_list = player.get_printable_list_pawns()
    x, y, pawn = None, None, None
    while(1):
        user_input = input("Player " + player.color.name + ", please play (" + pawn_list + ")\n")
        try:
            x, y, pawn = parse_input(user_input)
            break
        except InvalidInputError as e:
            print(e)

    player.check_has_pawn(pawn)
    is_a_win = board.play(x, y, pawn, player.color)
    player.remove(pawn)
    board.print()
    return is_a_win

@app.command()
def human():
    """Two humans play Quantik"""
    # Init the game elements
    board, player_cycle = init_game()
    player = next(player_cycle)

    print("Welcome to the Quantik game!")
    print("Example of a valid first move: 0 0 A\n")

    while(1):
        try:
            is_a_win = human_player_loop(board, player)
            if is_a_win:
                print("Congratulations, player " + player.color.name + " WINS !")
                break
        except game_elements.InvalidMoveError as e:
            print(e)
            continue
        player = next(player_cycle)
        if not board.have_possible_move(player.color):
            print("Player " + player.color.name + " has no possible move left, he loses!")
            break

@app.command()
def bot():
    """Play against a bot"""
    board, player_cycle = init_game()
    player = next(player_cycle)

    print("Welcome to the Quantik game!")
    print("Example of a valid first move: 0 0 A\n")
    
    user_input = input("Do you want to start (\033[1myes\033[0m/no)? ")
    answer = user_input.strip() == "" or user_input.strip() == "yes"
    if not answer:
        player = next(player_cycle)
        # The 1st move takes too much time to compute
        # Random move is OK, adds more fun for the player
        random.seed()
        pawn =  list(game_elements.Pawns)[random.randrange(4)]
        board.play(random.randrange(4), random.randrange(4), pawn, player.color)
        player.remove(pawn)
        board.print()
        player = next(player_cycle)

    while(1):
        try:
            is_a_win = False
            if player.color == game_elements.Colors.BLUE:
                # Human player's turn
                is_a_win = human_player_loop(board, player)
            else:
                # Bot's turn
                move = minmax.get_best_move(board, player, next(player_cycle))
                if move is None:
                    print("Player " + player.color.name + " gives up and loses.")
                    break
                (x,y,pawn) = move
                is_a_win = board.play(x, y, pawn, player.color)
                player.remove(pawn)
                board.print()

                next(player_cycle) # iterate to get back to other player
            if is_a_win:
                print("Congratulations, player " + player.color.name + " WINS !")
                break
        except game_elements.InvalidMoveError as e:
            print(e)
            continue
        player = next(player_cycle)
        if not board.have_possible_move(player.color):
            print("Player " + player.color.name + " has no possible move left, he loses!")
            break

@app.command()
def rules():
    """How to play"""
    print("""
          Welcome to Quantik, a game edited by Gigamic (I am not affiliated in any way with the editor).
          It is played by two players (BLUE and RED) on a 4*4 board, divided into 4 sections.
          Each player has 8 pawns, two of each type: A, A, B, B, C, C, D, D
          A player wins when he completes a row, column or section with 4 different pawns no matter their color.
          If it is not possible to play any pawn then the player loses.
          
          If there is a pawn on the board, then the opponent cannot play the same one in the same line, row or section.
          For example, if there is a blue 'A' on the board, then RED cannot play a 'A' in the same line, row or section. Blue
          can play a 'A' or any other pawn wherever they want.

          How to play?
          The computer expects an input in the format "x y pawn"
          x: index of the row (between 0 and 3)
          y: index of the column (between 0 and 3)
          pawn: which pawn to play, between A, B, C or D 
          Example of a valid input: 0 0 A
          Example of a board:
        """)
    board = game_elements.Board(board=[
        [(game_elements.Pawns.B, game_elements.Colors.RED), (game_elements.Pawns.A, game_elements.Colors.RED), (game_elements.Pawns.B, game_elements.Colors.RED), None],
        [None, None, None, None],
        [None, None, (game_elements.Pawns.A, game_elements.Colors.BLUE), (game_elements.Pawns.B, game_elements.Colors.BLUE)],
        [None, None, None, (game_elements.Pawns.D, game_elements.Colors.BLUE)]
    ])
    board.print()
    print(
        """Here the blue player only needs to play 3 2 C to win.
        """
    )

if __name__ == "__main__":
    app()
