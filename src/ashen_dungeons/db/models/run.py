from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ashen_dungeons.db.base import Base


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        CheckConstraint("status in ('active', 'won', 'lost', 'abandoned')", name="status_valid"),
        CheckConstraint("hp_current >= 0", name="hp_current_non_negative"),
        CheckConstraint("hp_max > 0", name="hp_max_positive"),
        CheckConstraint("mp_current >= 0", name="mp_current_non_negative"),
        CheckConstraint("mp_max >= 0", name="mp_max_non_negative"),
        CheckConstraint("gold >= 0", name="gold_non_negative"),
        CheckConstraint("xp >= 0", name="xp_non_negative"),
        CheckConstraint("level >= 1", name="level_minimum"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    save_slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("save_slots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    room_node_id: Mapped[str] = mapped_column(Text, nullable=False)
    hp_current: Mapped[int] = mapped_column(Integer, nullable=False)
    hp_max: Mapped[int] = mapped_column(Integer, nullable=False)
    mp_current: Mapped[int] = mapped_column(Integer, nullable=False)
    mp_max: Mapped[int] = mapped_column(Integer, nullable=False)
    gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    base_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    derived_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    seed: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    player: Mapped["Player"] = relationship(back_populates="runs")
    save_slot: Mapped["SaveSlot"] = relationship(back_populates="runs")
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    encounters: Mapped[list["Encounter"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    leaderboard_entries: Mapped[list["LeaderboardEntry"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
