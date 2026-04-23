from __future__ import annotations

from pathlib import Path

from .errors import ContentValidationError
from .registry import ContentRegistry
from .validators import load_json, validate_against_schema


def _index_by_id(records: list[dict], source_name: str) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for record in records:
        record_id = record["id"]
        if record_id in indexed:
            raise ContentValidationError(
                f"{source_name}: duplicate id '{record_id}'"
            )
        indexed[record_id] = record
    return indexed


def _validate_references(registry: ContentRegistry) -> None:
    for room_id, room in registry.rooms.items():
        enemy_pack_id = room.get("enemy_pack_id")
        if enemy_pack_id and enemy_pack_id not in registry.enemies:
            raise ContentValidationError(
                f"rooms.json: room '{room_id}' references unknown enemy '{enemy_pack_id}'"
            )

        reward_table_id = room.get("reward_table_id")
        if reward_table_id and reward_table_id not in registry.loot_tables:
            raise ContentValidationError(
                f"rooms.json: room '{room_id}' references unknown reward table '{reward_table_id}'"
            )

        for next_node in room.get("next_nodes", []):
            if next_node not in registry.rooms:
                raise ContentValidationError(
                    f"rooms.json: room '{room_id}' references unknown next node '{next_node}'"
                )

    for shop_id, shop in registry.shops.items():
        for item_id in shop.get("inventory_item_ids", []):
            if item_id not in registry.items:
                raise ContentValidationError(
                    f"shops.json: shop '{shop_id}' references unknown item '{item_id}'"
                )

    for loot_id, loot_table in registry.loot_tables.items():
        for reward in loot_table.get("entries", []):
            item_id = reward.get("item_id")
            if item_id and item_id not in registry.items:
                raise ContentValidationError(
                    f"loot_tables.json: loot table '{loot_id}' references unknown item '{item_id}'"
                )


def load_content(content_root: str | Path = "content") -> ContentRegistry:
    root = Path(content_root)
    schema_root = root / "schemas"

    def read_validated(data_filename: str, schema_filename: str):
        data = load_json(root / data_filename)
        schema = load_json(schema_root / schema_filename)
        validate_against_schema(data, schema, data_filename)
        return data

    classes = read_validated("classes.json", "classes.schema.json")
    rooms = read_validated("rooms.json", "rooms.schema.json")
    enemies = read_validated("enemies.json", "enemies.schema.json")
    bosses = read_validated("bosses.json", "bosses.schema.json")
    items = read_validated("items.json", "items.schema.json")
    loot_tables = read_validated("loot_tables.json", "loot_tables.schema.json")
    shops = read_validated("shops.json", "shops.schema.json")
    status_effects = read_validated("status_effects.json", "status_effects.schema.json")
    ui_text = read_validated("ui_text.json", "ui_text.schema.json")
    audio_map = read_validated("audio_map.json", "audio_map.schema.json")

    registry = ContentRegistry(
        classes=_index_by_id(classes["classes"], "classes.json"),
        rooms=_index_by_id(rooms["rooms"], "rooms.json"),
        enemies=_index_by_id(enemies["enemies"], "enemies.json"),
        bosses=_index_by_id(bosses["bosses"], "bosses.json"),
        items=_index_by_id(items["items"], "items.json"),
        loot_tables=_index_by_id(loot_tables["loot_tables"], "loot_tables.json"),
        shops=_index_by_id(shops["shops"], "shops.json"),
        status_effects=_index_by_id(status_effects["status_effects"], "status_effects.json"),
        ui_text=ui_text,
        audio_map=audio_map,
    )

    _validate_references(registry)
    return registry