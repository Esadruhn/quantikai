"""Console script for quantikai"""

import typer
import pathlib
from rich.console import Console

from quantikai import game, play, bot

app = typer.Typer()
console = Console()


@app.command(name="bot")
def bot_play():
    play.bot_play()


@app.command()
def human():
    play.human_play()


@app.command()
def rules():
    """How to play"""
    print(
        """
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
        """
    )
    board = game.Board(
        board=[
            [
                (game.Pawns.B, game.Colors.RED),
                (game.Pawns.A, game.Colors.RED),
                (game.Pawns.B, game.Colors.RED),
                None,
            ],
            [None, None, None, None],
            [
                None,
                None,
                (game.Pawns.A, game.Colors.BLUE),
                (game.Pawns.B, game.Colors.BLUE),
            ],
            [None, None, None, (game.Pawns.D, game.Colors.BLUE)],
        ]
    )
    board.print()
    print(
        """Here the blue player only needs to play 3 2 C to win.
        """
    )


@app.command()
def timer():
    bot.get_method_times()


@app.command()
def montecarlo():
    bot.montecarlo.generate_tree(
        path=pathlib.Path("montecarlo_tree.json"),
        board=game.Board(),
        current_player=game.Player(color=game.Colors.BLUE),
        other_player=game.Player(color=game.Colors.RED),
        iterations=50000,
        uct_cst=0.7,
        use_depth=True,
    )


if __name__ == "__main__":
    app()
