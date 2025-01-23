from flask import Flask, render_template, request, session, jsonify
import pathlib

from quantikai import game, bot

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
    move = request.get_json()
    board = game.Board.from_json(session["board"])
    human_player = game.Player.from_json(session["human_player"])
    move = game.Move(
        x=int(move["x"]),
        y=int(move["y"]),
        pawn=game.Pawns[move["pawn"]],
        color=human_player.color,
    )
    game_is_over = board.play(move)
    human_player.remove(move.pawn)

    session["board"] = board.to_json()
    session["human_player"] = human_player.to_json()

    return {
        "gameIsOver": game_is_over,
        "winMessage": PLAYER_WIN_MSG,
        "newMoves": [move.to_json()],
    }


@app.post("/bot")
def bot_turn():
    board = game.Board.from_json(session["board"])
    human_player = game.Player.from_json(session["human_player"])
    bot_player = game.Player.from_json(session["bot_player"])

    game_is_over = False
    win_message = None

    if not board.have_possible_move(bot_player.color):
        game_is_over = True
        win_message = PLAYER_WIN_MSG

    move = bot.get_best_move(board, bot_player, human_player)
    if move is None:
        game_is_over = True
        win_message = PLAYER_WIN_MSG
    else:
        game_is_over = board.play(move)
        bot_player.remove(move.pawn)
        if game_is_over or (
            not game_is_over and not board.have_possible_move(human_player.color)
        ):
            game_is_over = True
            win_message = BOT_WIN_MSG

    session["board"] = board.to_json()
    session["bot_player"] = bot_player.to_json()

    return {
        "gameIsOver": game_is_over,
        "winMessage": win_message,
        "newMoves": [move.to_json()],
    }
