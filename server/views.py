from flask import render_template, request, jsonify
from .app import app
from . import game


@app.route('/', methods=['POST'])
def bot():
    history = request.get_json()
    move, status = game.bot(history)
    return jsonify({'move': move, 'status': status})
