from flask import Blueprint, jsonify

bp = Blueprint("site", __name__)


@bp.get("/")
def home():
    return {
        "app": "Ashen Dungeons",
        "status": "ok",
        "message": "Home placeholder",
    }


@bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
    