from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ashen_dungeons.db.base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    local_profile_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    save_slots: Mapped[list["SaveSlot"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    runs: Mapped[list["Run"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    leaderboard_entries: Mapped[list["LeaderboardEntry"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
