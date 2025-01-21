from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pathlib

from quantikai import game, bot
from quantikai.game.enums import Pawns

PLAYER_WIN_MSG = "Congratulations, you win!"
BOT_WIN_MSG = "The bot wins!"

app = Flask(
    __name__,
    template_folder=pathlib.Path("web/templates"),
    static_folder=pathlib.Path("web/static"),
)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.errorhandler(game.InvalidMoveError)
def exception_handler(error):
    return jsonify(error=400, text=str(error)), 400


@app.route("/")
def home():
    human_player = game.Player(color=game.Colors.BLUE)
    board = game.Board()
    session["board"] = board.to_json()
    session["human_player"] = human_player.to_json()
    session["bot_player"] = game.Player(color=game.Colors.RED).to_json()
    return render_template("index.html")


@app.post("/")
def human_turn():
    # TODO proper request parsing
    move = request.get_json()
    board = game.Board.from_json(session["board"])
    human_player = game.Player.from_json(session["human_player"])
    game_is_over = board.play(
        x=int(move["x"]),
        y=int(move["y"]),
        pawn=move["pawn"],
        color=human_player.color,
    )
    human_player.remove(Pawns[move["pawn"]])

    session["board"] = board.to_json()
    session["human_player"] = human_player.to_json()

    human_move = {
        "x": int(move["x"]),
        "y": int(move["y"]),
        "pawn": move["pawn"],
        "color": human_player.color.name,
    }

    return {
        "game_is_over": game_is_over,
        "win_message": PLAYER_WIN_MSG if game_is_over else "",
        "new_moves": [human_move],
        "new_pawns": session["human_player"]["pawns"],
    }


@app.post("/bot")
def bot_turn():
    # TODO proper request parsing
    board = game.Board.from_json(session["board"])
    human_player = game.Player.from_json(session["human_player"])
    bot_player = game.Player.from_json(session["bot_player"])

    game_is_over = False
    win_message = None

    if not board.have_possible_move(bot_player.color):
        game_is_over = False
        win_message = PLAYER_WIN_MSG

    move = bot.get_best_move(board, bot_player, human_player)
    if move is None:
        game_is_over = True
        win_message = PLAYER_WIN_MSG
    else:
        game_is_over = board.play(*move)
        bot_player.remove(move[2])
        if game_is_over or (
            not game_is_over and not board.have_possible_move(human_player.color)
        ):
            game_is_over = True
            win_message = BOT_WIN_MSG

    session["board"] = board.to_json()
    session["bot_player"] = bot_player.to_json()

    bot_move = {
        "x": move[0],
        "y": move[1],
        "pawn": move[2].name,
        "color": bot_player.color.name,
    }

    return {
        "game_is_over": game_is_over,
        "win_message": win_message,
        "new_moves": [bot_move],
        "new_pawns": session["bot_player"]["pawns"],
    }
