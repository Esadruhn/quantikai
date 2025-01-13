"""Console script for game_elements."""
import typer
from rich.console import Console
import itertools

import game_elements

app = typer.Typer()
console = Console()

def parse_input(user_input: str):
    inp = user_input.strip().split()
    assert len(inp) == 3, "Wrong number of arguments, please enter 'x y pawn_name'"
    return int(inp[0]), int(inp[1]), game_elements.Pawns[inp[2]]


@app.command()
def main():
    """Console script for quantikai."""
    # Init the game elements
    board = game_elements.Board()
    players = [game_elements.Player(color=game_elements.Colors.BLUE),game_elements.Player(color=game_elements.Colors.RED)]

    player_cycle = itertools.cycle(players)
    player = next(player_cycle)

    print("Welcome to the Quantik game!")

    while(1):
        player.print_pawns()
        user_input = input("Player " + player.color.name + ", please play\n")
        try:
            x, y, pawn = parse_input(user_input)
            player.check_has_pawn(pawn)
            is_a_win = board.play(x, y, pawn, player.color)
            player.remove(pawn)
            board.print()
            if is_a_win:
                print("Congratulations, player " + player.color.name + " WINS !")
                break
        except Exception as e:
            print(e)
            continue
        player = next(player_cycle)
        if not board.have_possible_move(player.color):
            print("Player " + player.color.name + " has no possible move left, he loses!")
            break


if __name__ == "__main__":
    app()
