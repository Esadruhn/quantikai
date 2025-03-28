"""Console script for quantikai"""

import pathlib

import typer
from rich.console import Console

from quantikai import bot, game, play

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
        {
            (0, 0): (game.Pawns.B, game.Colors.RED),
            (0, 1): (game.Pawns.A, game.Colors.RED),
            (0, 2): (game.Pawns.B, game.Colors.RED),
            (2, 2): (game.Pawns.A, game.Colors.BLUE),
            (2, 3): (game.Pawns.B, game.Colors.BLUE),
            (3, 3): (game.Pawns.D, game.Colors.BLUE),
        }
    )
    board.print()
    print(
        """Here the blue player only needs to play 3 2 C to win.
        """
    )


@app.command()
def timer():
    bot.get_method_times()


@app.command("montecarlo")
def generate_montecarlo_tree(depth: int = 16):
    montecarlo_dir = pathlib.Path.cwd() / "montecarlo"
    montecarlo_dir.mkdir(parents=True, exist_ok=True)
    use_depth = True
    iterations = 25000  # 50000 OK, 100000 = process killed
    num_process = 5
    bot.montecarlo.generate_tree(
        path=montecarlo_dir,
        board=game.Board(),
        first_player=game.Player(color=game.Colors.BLUE),
        second_player=game.Player(color=game.Colors.RED),
        main_player_color=game.Colors.RED,
        iterations=iterations,
        use_depth=use_depth,
        max_depth=depth,
        num_process=num_process,
    )
    bot.montecarlo.generate_tree(
        path=montecarlo_dir,
        board=game.Board(),
        first_player=game.Player(color=game.Colors.BLUE),
        second_player=game.Player(color=game.Colors.RED),
        main_player_color=game.Colors.BLUE,
        iterations=iterations,
        use_depth=use_depth,
        max_depth=depth,
        num_process=num_process,
    )
    bot.montecarlo.generate_tree(
        path=montecarlo_dir,
        board=game.Board(),
        first_player=game.Player(color=game.Colors.RED),
        second_player=game.Player(color=game.Colors.BLUE),
        main_player_color=game.Colors.RED,
        iterations=iterations,
        use_depth=use_depth,
        max_depth=depth,
        num_process=num_process,
    )
    bot.montecarlo.generate_tree(
        path=montecarlo_dir,
        board=game.Board(),
        first_player=game.Player(color=game.Colors.RED),
        second_player=game.Player(color=game.Colors.BLUE),
        main_player_color=game.Colors.BLUE,
        iterations=iterations,
        use_depth=use_depth,
        max_depth=depth,
        num_process=num_process,
    )


if __name__ == "__main__":
    app()
