from dataclasses import dataclass


@dataclass(slots=True)
class ContentRegistry:
    classes: dict
    rooms: dict
    enemies: dict
    bosses: dict
    items: dict
    loot_tables: dict
    shops: dict
    status_effects: dict
    ui_text: dict
    audio_map: dict