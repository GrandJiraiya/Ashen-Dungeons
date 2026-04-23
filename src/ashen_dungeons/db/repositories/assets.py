from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from ashen_dungeons.db.models.asset_manifest import AssetManifest

from .base import BaseRepository


class AssetRepository(BaseRepository):
    def get(self, asset_id):
        return self.session.get(AssetManifest, asset_id)

    def get_by_key(self, asset_key: str):
        stmt = select(AssetManifest).where(AssetManifest.asset_key == asset_key)
        return self.session.scalars(stmt).first()

    def list_by_type(self, asset_type: str):
        stmt = (
            select(AssetManifest)
            .where(AssetManifest.asset_type == asset_type)
            .order_by(AssetManifest.asset_key.asc())
        )
        return list(self.session.scalars(stmt).all())

    def create_asset(
        self,
        *,
        asset_key: str,
        asset_type: str,
        logical_group: str,
        storage_url: str,
        checksum: str | None = None,
        is_placeholder: bool = True,
    ) -> AssetManifest:
        asset = AssetManifest(
            id=uuid4(),
            asset_key=asset_key,
            asset_type=asset_type,
            logical_group=logical_group,
            storage_url=storage_url,
            checksum=checksum,
            is_placeholder=is_placeholder,
        )
        self.add(asset)
        self.flush()
        return asset