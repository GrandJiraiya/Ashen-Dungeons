from __future__ import annotations

import copy
import json
import random
from pathlib import Path
from typing import Any


class GameService:
    def __init__(self, content, data_root: str = "local_data") -> None:
        self.content = content
        self.data_root = Path(data_root)
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.saves_path = self.data_root / "saves.json"
        self.leaderboard_path = self.data_root / "leaderboard.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        if not self.saves_path.exists():
            self._write_json(self.saves_path, {"slots": {}})
        if not self.leaderboard_path.exists():
            self._write_json(self.leaderboard_path, {"entries": []})

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _weighted_pick(self, entries: list[dict]) -> dict:
        total = sum(max(1, int(e.get("weight", 1))) for e in entries)
        roll = random.randint(1, total)
        running = 0
        for entry in entries:
            running += max(1, int(entry.get("weight", 1)))
            if roll <= running:
                return entry
        return entries[-1]

    def get_classes(self) -> list[dict]:
        return list(self.content.classes.values())

    def list_slots(self) -> dict[str, Any]:
        return self._read_json(self.saves_path)["slots"]

    def get_slot(self, slot_id: str) -> dict | None:
        return self.list_slots().get(slot_id)

    def create_run(self, slot_id: str, class_id: str, player_name: str) -> dict:
        class_def = self.content.classes[class_id]
        stats = class_def["base_stats"]
        room = self.content.rooms["room_01"]
        state = {
            "slot_id": slot_id,
            "player_name": player_name or "Wanderer",
            "class_id": class_id,
            "class_name": class_def["name"],
            "room_id": "room_01",
            "visited_rooms": [],
            "status": "active",
            "level": 1,
            "xp": 0,
            "gold": 0,
            "score": 0,
            "equipment": {"weapon": None, "armor": None, "trinket": None},
            "inventory": [{"item_id": "healing_draught", "quantity": 1}],
            "skills": list(class_def["starting_skills"]),
            "base_stats": copy.deepcopy(stats),
            "hp": stats["hp"],
            "mp": stats["mp"],
            "pending_reward": None,
            "current_enemy": None,
            "message": f"You descend into {room['title']}.",
            "last_battle_won": False,
        }
        self._advance_into_room(state, room)
        self.save_slot(slot_id, state)
        return state

    def save_slot(self, slot_id: str, state: dict) -> None:
        data = self._read_json(self.saves_path)
        data["slots"][slot_id] = state
        self._write_json(self.saves_path, data)

    def delete_slot(self, slot_id: str) -> None:
        data = self._read_json(self.saves_path)
        data["slots"].pop(slot_id, None)
        self._write_json(self.saves_path, data)

    def leaderboard(self) -> list[dict]:
        entries = self._read_json(self.leaderboard_path)["entries"]
        return sorted(entries, key=lambda e: (-e["score"], -e["rooms_cleared"], e["player_name"]))

    def submit_score(self, state: dict) -> None:
        if state.get("status") not in {"won", "lost"}:
            return
        data = self._read_json(self.leaderboard_path)
        entry = {
            "player_name": state["player_name"],
            "class_name": state["class_name"],
            "score": state["score"],
            "rooms_cleared": len(state["visited_rooms"]),
            "result": state["status"],
        }
        data["entries"].append(entry)
        self._write_json(self.leaderboard_path, data)

    def derived_stats(self, state: dict) -> dict:
        stats = copy.deepcopy(state["base_stats"])
        for slot, item_id in state["equipment"].items():
            if item_id:
                item = self.content.items[item_id]
                for key, value in item.get("bonus", {}).items():
                    stats[key] = stats.get(key, 0) + value
        return stats

    def skill_data(self, skill_id: str) -> dict:
        if skill_id == "guard_slash":
            return {"name": "Guard Slash", "mp_cost": 5, "power": 1.5}
        if skill_id == "ember_hex":
            return {"name": "Ember Hex", "mp_cost": 7, "power": 1.9}
        if skill_id == "shadow_lunge":
            return {"name": "Shadow Lunge", "mp_cost": 6, "power": 1.7}
        return {"name": skill_id, "mp_cost": 5, "power": 1.4}

    def _advance_into_room(self, state: dict, room: dict) -> None:
        room_type = room["type"]
        state["current_room"] = room
        state["last_battle_won"] = False
        if room_type in {"battle", "boss"}:
            enemy = copy.deepcopy(self.content.enemies[room["enemy_pack_id"]])
            state["current_enemy"] = enemy
            state["message"] = f"A {enemy['name']} bars your path in {room['title']}."
        elif room_type == "rest":
            stats = self.derived_stats(state)
            state["hp"] = min(stats["hp"], state["hp"] + 30)
            state["mp"] = min(stats["mp"], state["mp"] + 20)
            state["current_enemy"] = None
            state["message"] = "You rest in silence and recover strength."
        elif room_type == "merchant":
            state["current_enemy"] = None
            state["message"] = "A cautious merchant offers wares."
        elif room_type == "event":
            state["current_enemy"] = None
            if room.get("event_id") == "ember_shrine":
                state["mp"] += 10
                state["message"] = "The shrine burns your skin but restores 10 MP."
            elif room.get("event_id") == "blood_well":
                state["hp"] = max(1, state["hp"] - 10)
                state["gold"] += 20
                state["message"] = "You feed the well and gain 20 gold, losing 10 HP."
        else:
            state["current_enemy"] = None
            state["message"] = room["title"]

    def _gain_xp(self, state: dict, amount: int) -> None:
        state["xp"] += amount
        threshold = state["level"] * 50
        if state["xp"] >= threshold:
            state["xp"] -= threshold
            state["level"] += 1
            state["base_stats"]["hp"] += 10
            state["base_stats"]["mp"] += 5
            state["base_stats"]["attack"] += 2
            state["base_stats"]["defense"] += 1
            state["base_stats"]["speed"] += 1
            stats = self.derived_stats(state)
            state["hp"] = stats["hp"]
            state["mp"] = stats["mp"]
            state["message"] += f" You reached level {state['level']}!"

    def _generate_reward(self, reward_table_id: str) -> dict:
        table = self.content.loot_tables[reward_table_id]
        pick = self._weighted_pick(table["entries"])
        return pick

    def attack(self, state: dict) -> dict:
        enemy = state["current_enemy"]
        if not enemy or state["status"] != "active":
            return state
        stats = self.derived_stats(state)
        dmg = max(1, stats["attack"] - enemy["defense"] + random.randint(0, 4))
        enemy["hp"] -= dmg
        message = f"You strike {enemy['name']} for {dmg} damage."
        if enemy["hp"] <= 0:
            state["message"] = message
            self._win_battle(state)
            return state
        return self._enemy_turn(state, message)

    def use_skill(self, state: dict, skill_id: str) -> dict:
        enemy = state["current_enemy"]
        if not enemy or state["status"] != "active":
            return state
        skill = self.skill_data(skill_id)
        if state["mp"] < skill["mp_cost"]:
            state["message"] = f"Not enough MP for {skill['name']}."
            return state
        state["mp"] -= skill["mp_cost"]
        stats = self.derived_stats(state)
        dmg = max(1, int(stats["attack"] * skill["power"]) - enemy["defense"] + random.randint(0, 4))
        enemy["hp"] -= dmg
        message = f"You cast {skill['name']} for {dmg} damage."
        if enemy["hp"] <= 0:
            state["message"] = message
            self._win_battle(state)
            return state
        return self._enemy_turn(state, message)

    def defend(self, state: dict) -> dict:
        if not state["current_enemy"] or state["status"] != "active":
            return state
        state["defending"] = True
        return self._enemy_turn(state, "You brace for the incoming blow.")

    def use_item(self, state: dict, item_id: str) -> dict:
        inv = state["inventory"]
        entry = next((x for x in inv if x["item_id"] == item_id and x["quantity"] > 0), None)
        if entry is None:
            state["message"] = "You do not have that item."
            return state
        item = self.content.items[item_id]
        entry["quantity"] -= 1
        if entry["quantity"] <= 0:
            inv.remove(entry)
        stats = self.derived_stats(state)
        if item.get("heal"):
            state["hp"] = min(stats["hp"], state["hp"] + item["heal"])
            state["message"] = f"You use {item['name']} and recover {item['heal']} HP."
        elif item.get("mp_restore"):
            state["mp"] = min(stats["mp"], state["mp"] + item["mp_restore"])
            state["message"] = f"You use {item['name']} and recover {item['mp_restore']} MP."
        if state.get("current_enemy"):
            return self._enemy_turn(state, state["message"])
        return state

    def buy_item(self, state: dict, item_id: str) -> dict:
        room = state.get("current_room", {})
        if room.get("type") != "merchant":
            state["message"] = "There is no merchant here."
            return state
        shop = self.content.shops[room["shop_id"]]
        if item_id not in shop["inventory_item_ids"]:
            state["message"] = "That item is not sold here."
            return state
        item = self.content.items[item_id]
        price = item.get("price", 10)
        if state["gold"] < price:
            state["message"] = "Not enough gold."
            return state
        state["gold"] -= price
        inv_entry = next((x for x in state["inventory"] if x["item_id"] == item_id), None)
        if inv_entry:
            inv_entry["quantity"] += 1
        else:
            state["inventory"].append({"item_id": item_id, "quantity": 1})
        state["message"] = f"You bought {item['name']} for {price} gold."
        return state

    def equip_item(self, state: dict, item_id: str) -> dict:
        item = self.content.items[item_id]
        slot = item.get("slot")
        if not slot:
            state["message"] = "That item cannot be equipped."
            return state
        has_item = next((x for x in state["inventory"] if x["item_id"] == item_id and x["quantity"] > 0), None)
        if not has_item:
            state["message"] = "You do not have that item."
            return state
        state["equipment"][slot] = item_id
        stats = self.derived_stats(state)
        state["hp"] = min(state["hp"], stats["hp"])
        state["mp"] = min(state["mp"], stats["mp"])
        state["message"] = f"You equipped {item['name']}."
        return state

    def move_next(self, state: dict) -> dict:
        room = state["current_room"]
        next_nodes = room.get("next_nodes", [])
        if state.get("pending_reward"):
            state["message"] = "Choose your reward first."
            return state
        if room.get("type") in {"battle", "boss"} and state.get("current_enemy"):
            state["message"] = "You must finish the fight first."
            return state
        if not next_nodes:
            if state["status"] == "won":
                state["message"] = "You have cleared the dungeon."
            return state
        if room["id"] not in state["visited_rooms"]:
            state["visited_rooms"].append(room["id"])
        next_room = self.content.rooms[next_nodes[0]]
        state["room_id"] = next_room["id"]
        self._advance_into_room(state, next_room)
        return state

    def choose_reward(self, state: dict) -> dict:
        reward = state.get("pending_reward")
        if not reward:
            return state
        if reward["type"] == "gold":
            state["gold"] += reward["amount"]
            state["message"] = f"You gain {reward['amount']} gold."
        elif reward["type"] == "item":
            item = self.content.items[reward["item_id"]]
            inv_entry = next((x for x in state["inventory"] if x["item_id"] == reward["item_id"]), None)
            if inv_entry:
                inv_entry["quantity"] += 1
            else:
                state["inventory"].append({"item_id": reward["item_id"], "quantity": 1})
            state["message"] = f"You obtain {item['name']}."
        state["pending_reward"] = None
        return state

    def _enemy_turn(self, state: dict, intro_message: str) -> dict:
        enemy = state["current_enemy"]
        stats = self.derived_stats(state)
        dmg = max(1, enemy["attack"] - stats["defense"] + random.randint(0, 3))
        if state.pop("defending", False):
            dmg = max(1, dmg // 2)
        state["hp"] -= dmg
        if state["hp"] <= 0:
            state["hp"] = 0
            state["status"] = "lost"
            state["message"] = f"{intro_message} {enemy['name']} hits you for {dmg}. You fall in the dark."
            return state
        state["message"] = f"{intro_message} {enemy['name']} hits you for {dmg}."
        return state

    def _win_battle(self, state: dict) -> None:
        enemy = state["current_enemy"]
        state["gold"] += enemy.get("gold", 0)
        self._gain_xp(state, enemy.get("xp", 0))
        state["score"] += enemy.get("xp", 0) + enemy.get("gold", 0)
        room = state["current_room"]
        reward = self._generate_reward(room["reward_table_id"])
        state["pending_reward"] = reward
        state["current_enemy"] = None
        state["last_battle_won"] = True
        if room["id"] not in state["visited_rooms"]:
            state["visited_rooms"].append(room["id"])
        if room["type"] == "boss":
            state["status"] = "won"
            state["message"] += " The Ashen Warden falls. The dungeon is conquered."
        else:
            state["message"] += f" Victory. Gain {enemy.get('gold',0)} gold and {enemy.get('xp',0)} XP."

    def view_context(self, state: dict) -> dict:
        stats = self.derived_stats(state)
        room = state.get("current_room", {})
        merchant_items = []
        if room.get("type") == "merchant":
            shop = self.content.shops[room["shop_id"]]
            merchant_items = [self.content.items[i] for i in shop["inventory_item_ids"]]
        inventory_view = []
        for entry in state["inventory"]:
            item = self.content.items[entry["item_id"]]
            inventory_view.append({
                "id": item["id"],
                "name": item["name"],
                "kind": item["kind"],
                "quantity": entry["quantity"],
                "slot": item.get("slot"),
            })
        reward_view = None
        if state.get("pending_reward"):
            r = state["pending_reward"]
            reward_view = dict(r)
            if r["type"] == "item":
                reward_view["item_name"] = self.content.items[r["item_id"]]["name"]
        return {
            "state": state,
            "stats": stats,
            "enemy": state.get("current_enemy"),
            "room": room,
            "merchant_items": merchant_items,
            "inventory_view": inventory_view,
            "reward_view": reward_view,
            "skills": [self.skill_data(s) | {"id": s} for s in state["skills"]],
            "classes": self.get_classes(),
            "leaderboard": self.leaderboard(),
        }
