"""Console script for quantikai"""

import typer
from rich.console import Console
import timeit

from quantikai import game, minmax, play

app = typer.Typer()
console = Console()


@app.command()
def bot():
    play.bot_play()


@app.command()
def human():
    play.human_play()


@app.command()
def timer():
    print(timeit.timeit(play.botvsbot_play, number=10))


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


if __name__ == "__main__":
    app()
