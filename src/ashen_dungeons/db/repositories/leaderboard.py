from __future__ import annotations

from uuid import uuid4

from sqlalchemy import desc, select

from ashen_dungeons.db.models.leaderboard_entry import LeaderboardEntry

from .base import BaseRepository


class LeaderboardRepository(BaseRepository):
    def get_by_run_id(self, run_id):
        stmt = select(LeaderboardEntry).where(LeaderboardEntry.run_id == run_id)
        return self.session.scalars(stmt).first()

    def submit_entry(
        self,
        *,
        player_id,
        run_id,
        display_name_snapshot: str,
        score: int,
        floors_cleared: int,
        class_id: str,
        result: str,
    ) -> LeaderboardEntry:
        entry = LeaderboardEntry(
            id=uuid4(),
            player_id=player_id,
            run_id=run_id,
            display_name_snapshot=display_name_snapshot,
            score=score,
            floors_cleared=floors_cleared,
            class_id=class_id,
            result=result,
        )
        self.add(entry)
        self.flush()
        return entry

    def top_entries(self, limit: int = 100):
        stmt = (
            select(LeaderboardEntry)
            .order_by(
                desc(LeaderboardEntry.score),
                desc(LeaderboardEntry.floors_cleared),
                LeaderboardEntry.created_at.asc(),
            )
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())