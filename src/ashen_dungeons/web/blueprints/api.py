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
    
@bp.post("/runs")
def create_run():
    current_player = _get_current_player_or_error()
    if isinstance(current_player, tuple):
        return current_player

    payload = request.get_json(silent=True) or {}

    class_id = str(payload.get("class_id", "")).strip()
    if not class_id:
        return jsonify({"error": "class_id_required"}), 400

    save_slot_id = payload.get("save_slot_id")
    try:
        parsed_save_slot_id = UUID(str(save_slot_id))
    except (TypeError, ValueError):
        return jsonify({"error": "valid_save_slot_id_required"}), 400

    registry = current_app.extensions["content_registry"]
    class_def = registry.classes.get(class_id)

    if class_def is None:
        return jsonify({"error": "invalid_class_id"}), 400

    base_stats = dict(class_def["base_stats"])
    derived_stats = dict(base_stats)

    try:
        hp_max = int(base_stats["hp"])
        mp_max = int(base_stats["mp"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "class_stats_invalid"}), 500

    room_node_id = _resolve_start_room_node_id(registry)

    db = get_db_session()
    save_slots = SaveSlotRepository(db)
    runs = RunRepository(db)

    save_slot = save_slots.get_for_player_by_id(
        current_player.id,
        parsed_save_slot_id,
    )

    if save_slot is None:
        return jsonify({"error": "save_slot_not_found"}), 404

    try:
        run = runs.create(
            player_id=current_player.id,
            save_slot_id=save_slot.id,
            class_id=class_id,
            room_node_id=room_node_id,
            hp_current=hp_max,
            hp_max=hp_max,
            mp_current=mp_max,
            mp_max=mp_max,
            base_stats=base_stats,
            derived_stats=derived_stats,
        )

        save_slots.set_last_run(save_slot, run.id)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    return jsonify({"run": _serialize_run(run)}), 201
    
def _resolve_start_room_node_id(registry) -> str:
    if "start" in registry.rooms:
        return "start"

    first_room_id = next(iter(registry.rooms), None)
    if first_room_id:
        return first_room_id

    return "start"


def _serialize_run(run) -> dict:
    return {
        "id": str(run.id),
        "player_id": str(run.player_id),
        "save_slot_id": str(run.save_slot_id),
        "class_id": run.class_id,
        "status": run.status,
        "floor_number": run.floor_number,
        "room_node_id": run.room_node_id,
        "hp_current": run.hp_current,
        "hp_max": run.hp_max,
        "mp_current": run.mp_current,
        "mp_max": run.mp_max,
        "gold": run.gold,
        "xp": run.xp,
        "level": run.level,
        "base_stats": run.base_stats,
        "derived_stats": run.derived_stats,
        "seed": run.seed,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "ended_at": run.ended_at.isoformat() if run.ended_at else None,
    }
    