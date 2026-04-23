from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ashen_dungeons.db.base import Base


class AssetManifest(Base):
    __tablename__ = "asset_manifest"
    __table_args__ = (
        CheckConstraint("asset_type in ('image', 'music', 'sfx')", name="asset_type_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    asset_type: Mapped[str] = mapped_column(Text, nullable=False)
    logical_group: Mapped[str] = mapped_column(Text, nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_placeholder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
