from __future__ import annotations
from uuid import UUID
import secrets
from ashen_dungeons.db.repositories import (

    PlayerRepository,

    RunRepository,

    SaveSlotRepository,

)

from flask import Blueprint, jsonify, request, session as flask_session
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ashen_dungeons.db.repositories import PlayerRepository
from ashen_dungeons.db.session import get_db_session

bp = Blueprint("api", __name__, url_prefix="/api")


DEFAULT_DISPLAY_NAME = "Wanderer"
MAX_DISPLAY_NAME_LENGTH = 32
MIN_PROFILE_KEY_LENGTH = 16
MAX_PROFILE_KEY_LENGTH = 128


@bp.get("/ping")
def ping():
    return jsonify({"message": "api ok"}), 200


@bp.get("/db-ping")
def db_ping():
    session = get_db_session()
    result = session.execute(text("SELECT 1")).scalar_one()
    return jsonify({"db": result}), 200


@bp.post("/profile/init")
def init_profile():
    payload = request.get_json(silent=True) or {}

    local_profile_key = _resolve_or_create_local_profile_key(payload)
    display_name = _clean_display_name(
        payload.get("display_name"),
        default=DEFAULT_DISPLAY_NAME,
    )

    db = get_db_session()
    players = PlayerRepository(db)

    try:
        player = players.get_by_local_profile_key(local_profile_key)
        created = False

        if player is None:
            player = players.create(
                display_name=display_name,
                local_profile_key=local_profile_key,
            )
            created = True
        else:
            players.touch_last_seen(player)

        flask_session["local_profile_key"] = local_profile_key
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    status_code = 201 if created else 200

    return jsonify(
        {
            "player": _serialize_player(player),
            "local_profile_key": local_profile_key,
            "created": created,
        }
    ), status_code


@bp.get("/profile/me")
def get_profile():
    local_profile_key = _get_current_local_profile_key()
    if local_profile_key is None:
        return jsonify({"error": "profile_not_initialized"}), 401

    db = get_db_session()
    players = PlayerRepository(db)
    player = players.get_by_local_profile_key(local_profile_key)

    if player is None:
        return jsonify({"error": "profile_not_found"}), 404

    return jsonify(
        {
            "player": _serialize_player(player),
            "local_profile_key": local_profile_key,
        }
    ), 200


@bp.patch("/profile/me")
def update_profile():
    local_profile_key = _get_current_local_profile_key()
    if local_profile_key is None:
        return jsonify({"error": "profile_not_initialized"}), 401

    payload = request.get_json(silent=True) or {}
    display_name = _clean_display_name(payload.get("display_name"), default=None)

    if display_name is None:
        return jsonify({"error": "display_name_required"}), 400

    db = get_db_session()
    players = PlayerRepository(db)
    player = players.get_by_local_profile_key(local_profile_key)

    if player is None:
        return jsonify({"error": "profile_not_found"}), 404

    try:
        players.update_display_name(player, display_name)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return jsonify(
        {
            "player": _serialize_player(player),
            "local_profile_key": local_profile_key,
        }
    ), 200


def _resolve_or_create_local_profile_key(payload: dict) -> str:
    candidate = (
        payload.get("local_profile_key")
        or request.headers.get("X-Local-Profile-Key")
        or flask_session.get("local_profile_key")
    )

    if candidate:
        candidate = str(candidate).strip()
        if MIN_PROFILE_KEY_LENGTH <= len(candidate) <= MAX_PROFILE_KEY_LENGTH:
            return candidate

    return secrets.token_urlsafe(32)


def _get_current_local_profile_key() -> str | None:
    candidate = (
        request.headers.get("X-Local-Profile-Key")
        or flask_session.get("local_profile_key")
    )

    if not candidate:
        return None

    candidate = str(candidate).strip()
    if not candidate:
        return None

    return candidate


def _clean_display_name(value, default: str | None) -> str | None:
    if value is None:
        return default

    cleaned = str(value).strip()
    if not cleaned:
        return default

    return cleaned[:MAX_DISPLAY_NAME_LENGTH]


def _serialize_player(player) -> dict:
    return {
        "id": str(player.id),
        "display_name": player.display_name,
        "created_at": player.created_at.isoformat() if player.created_at else None,
        "updated_at": player.updated_at.isoformat() if player.updated_at else None,
        "last_seen_at": player.last_seen_at.isoformat() if player.last_seen_at else None,
    }