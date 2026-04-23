from flask import Blueprint, jsonify
from sqlalchemy import text

from ashen_dungeons.db.session import get_db_session

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/ping")
def ping():
    return jsonify({"message": "api ok"}), 200


@bp.get("/db-ping")
def db_ping():
    session = get_db_session()
    result = session.execute(text("SELECT 1")).scalar_one()
    return jsonify({"db": result}), 200