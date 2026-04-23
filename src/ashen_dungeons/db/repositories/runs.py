from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from ashen_dungeons.db.models.run import Run

from .base import BaseRepository


class RunRepository(BaseRepository):
    def get(self, run_id):
        return self.session.get(Run, run_id)

    def list_for_player(self, player_id):
        stmt = (
            select(Run)
            .where(Run.player_id == player_id)
            .order_by(Run.started_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def list_for_save_slot(self, save_slot_id):
        stmt = (
            select(Run)
            .where(Run.save_slot_id == save_slot_id)
            .order_by(Run.started_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def create(
        self,
        *,
        player_id,
        save_slot_id,
        class_id: str,
        room_node_id: str,
        hp_current: int,
        hp_max: int,
        mp_current: int,
        mp_max: int,
        base_stats: dict,
        derived_stats: dict,
    ) -> Run:
        run = Run(
            id=uuid4(),
            player_id=player_id,
            save_slot_id=save_slot_id,
            class_id=class_id,
            status="active",
            floor_number=1,
            room_node_id=room_node_id,
            hp_current=hp_current,
            hp_max=hp_max,
            mp_current=mp_current,
            mp_max=mp_max,
            gold=0,
            xp=0,
            level=1,
            base_stats=base_stats,
            derived_stats=derived_stats,
        )
        self.add(run)
        self.flush()
        return run

    def update_state(self, run: Run, **fields) -> Run:
        for key, value in fields.items():
            setattr(run, key, value)
        self.flush()
        return run

    def mark_finished(self, run: Run, status: str) -> Run:
        run.status = status
        self.flush()
        return run