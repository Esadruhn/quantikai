"""Console script for game_elements."""
import typer
from rich.console import Console
import itertools

from quantikai import game_elements, minmax

app = typer.Typer()
console = Console()

def parse_input(user_input: str):
    inp = user_input.strip().split()
    assert len(inp) == 3, "Wrong number of arguments, please enter 'x y pawn_name'"
    return int(inp[0]), int(inp[1]), game_elements.Pawns[inp[2]]

def init_game():
    board = game_elements.Board()
    players = [game_elements.Player(color=game_elements.Colors.BLUE),game_elements.Player(color=game_elements.Colors.RED)]

    player_cycle = itertools.cycle(players)
    return board, player_cycle

def human_player_loop(board, player):
    player.print_pawns()
    user_input = input("Player " + player.color.name + ", please play\n")
    x, y, pawn = parse_input(user_input)
    player.check_has_pawn(pawn)
    is_a_win = board.play(x, y, pawn, player.color)
    player.remove(pawn)
    board.print()
    return is_a_win


def main():
    """Console script for quantikai."""
    # Init the game elements
    board, player_cycle = init_game()
    player = next(player_cycle)

    print("Welcome to the Quantik game!")

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
def play_against_bot():
    board, player_cycle = init_game()
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

if __name__ == "__main__":
    app()
