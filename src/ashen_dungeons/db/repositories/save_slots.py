from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from ashen_dungeons.db.models.save_slot import SaveSlot

from .base import BaseRepository


class SaveSlotRepository(BaseRepository):
    def get(self, save_slot_id):
        return self.session.get(SaveSlot, save_slot_id)

    def list_for_player(self, player_id):
        stmt = (
            select(SaveSlot)
            .where(SaveSlot.player_id == player_id)
            .order_by(SaveSlot.slot_index.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get_for_player_slot(self, player_id, slot_index: int):
        stmt = select(SaveSlot).where(
            SaveSlot.player_id == player_id,
            SaveSlot.slot_index == slot_index,
        )
        return self.session.scalars(stmt).first()

    def create_slot(self, player_id, slot_index: int, title: str) -> SaveSlot:
        slot = SaveSlot(
            id=uuid4(),
            player_id=player_id,
            slot_index=slot_index,
            title=title,
            is_active=True,
        )
        self.add(slot)
        self.flush()
        return slot

    def set_last_run(self, slot: SaveSlot, run_id) -> SaveSlot:
        slot.last_run_id = run_id
        slot.updated_at = datetime.now(timezone.utc)
        self.flush()
        return slot