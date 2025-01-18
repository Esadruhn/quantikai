from flask import Flask, render_template
import pathlib

app = Flask(__name__, template_folder=pathlib.Path("web/templates"), static_folder=pathlib.Path("web/static"))

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.post("/")
def login_post():
    return "<p>Hello, World!</p>"