from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from ashen_dungeons.db.models.player import Player

from .base import BaseRepository


class PlayerRepository(BaseRepository):
    def get(self, player_id):
        return self.session.get(Player, player_id)

    def get_by_local_profile_key(self, local_profile_key: str):
        stmt = select(Player).where(Player.local_profile_key == local_profile_key)
        return self.session.scalars(stmt).first()

    def create(self, display_name: str, local_profile_key: str) -> Player:
        player = Player(
            id=uuid4(),
            display_name=display_name,
            local_profile_key=local_profile_key,
        )
        self.add(player)
        self.flush()
        return player

    def touch_last_seen(self, player: Player) -> Player:
        player.last_seen_at = datetime.now(timezone.utc)
        self.flush()
        return player

    def update_display_name(self, player: Player, display_name: str) -> Player:
        player.display_name = display_name
        player.updated_at = datetime.now(timezone.utc)
        self.flush()
        return player