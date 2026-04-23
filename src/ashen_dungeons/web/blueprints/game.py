from flask import Blueprint

bp = Blueprint("game", __name__, url_prefix="/game")


@bp.get("/")
def game_index():
    return {
        "section": "game",
        "message": "Game blueprint placeholder",
    }
    