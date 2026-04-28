"""Initial schema

Revision ID: 20260428_0001
Revises:
Create Date: 2026-04-28 21:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260428_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asset_manifest",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_key", sa.Text(), nullable=False),
        sa.Column("asset_type", sa.Text(), nullable=False),
        sa.Column("logical_group", sa.Text(), nullable=False),
        sa.Column("storage_url", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=True),
        sa.Column("is_placeholder", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("asset_type in ('image', 'music', 'sfx')", name=op.f("ck_asset_manifest_asset_type_valid")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_asset_manifest")),
        sa.UniqueConstraint("asset_key", name=op.f("uq_asset_manifest_asset_key")),
    )

    op.create_table(
        "healthcheck_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_healthcheck_records")),
    )

    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("local_profile_key", sa.Text(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_players")),
        sa.UniqueConstraint("local_profile_key", name=op.f("uq_players_local_profile_key")),
    )

    op.create_table(
        "save_slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slot_index", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE", name=op.f("fk_save_slots_player_id_players")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_save_slots")),
        sa.UniqueConstraint("player_id", "slot_index", name="uq_save_slots_player_id"),
    )
    op.create_index(op.f("ix_save_slots_player_id"), "save_slots", ["player_id"], unique=False)

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("save_slot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("floor_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("room_node_id", sa.Text(), nullable=False),
        sa.Column("hp_current", sa.Integer(), nullable=False),
        sa.Column("hp_max", sa.Integer(), nullable=False),
        sa.Column("mp_current", sa.Integer(), nullable=False),
        sa.Column("mp_max", sa.Integer(), nullable=False),
        sa.Column("gold", sa.Integer(), server_default="0", nullable=False),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("base_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("derived_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("seed", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status in ('active', 'won', 'lost', 'abandoned')", name=op.f("ck_runs_status_valid")),
        sa.CheckConstraint("hp_current >= 0", name=op.f("ck_runs_hp_current_non_negative")),
        sa.CheckConstraint("hp_max > 0", name=op.f("ck_runs_hp_max_positive")),
        sa.CheckConstraint("mp_current >= 0", name=op.f("ck_runs_mp_current_non_negative")),
        sa.CheckConstraint("mp_max >= 0", name=op.f("ck_runs_mp_max_non_negative")),
        sa.CheckConstraint("gold >= 0", name=op.f("ck_runs_gold_non_negative")),
        sa.CheckConstraint("xp >= 0", name=op.f("ck_runs_xp_non_negative")),
        sa.CheckConstraint("level >= 1", name=op.f("ck_runs_level_minimum")),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE", name=op.f("fk_runs_player_id_players")),
        sa.ForeignKeyConstraint(["save_slot_id"], ["save_slots.id"], ondelete="CASCADE", name=op.f("fk_runs_save_slot_id_save_slots")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_runs")),
    )
    op.create_index(op.f("ix_runs_player_id"), "runs", ["player_id"], unique=False)
    op.create_index(op.f("ix_runs_save_slot_id"), "runs", ["save_slot_id"], unique=False)
    op.create_index(op.f("ix_runs_started_at"), "runs", ["started_at"], unique=False)
    op.create_index(op.f("ix_runs_status"), "runs", ["status"], unique=False)

    op.create_table(
        "encounters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.Text(), nullable=False),
        sa.Column("encounter_type", sa.Text(), nullable=False),
        sa.Column("enemy_pack_id", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("log_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.CheckConstraint("encounter_type in ('battle', 'event', 'merchant', 'rest', 'boss')", name=op.f("ck_encounters_encounter_type_valid")),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE", name=op.f("fk_encounters_run_id_runs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_encounters")),
    )
    op.create_index(op.f("ix_encounters_run_id"), "encounters", ["run_id"], unique=False)

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", sa.Text(), nullable=False),
        sa.Column("item_type", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("rarity", sa.Text(), nullable=False),
        sa.Column("equipped_slot", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.CheckConstraint("quantity > 0", name=op.f("ck_inventory_items_quantity_positive")),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE", name=op.f("fk_inventory_items_run_id_runs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_items")),
    )
    op.create_index(op.f("ix_inventory_items_run_id"), "inventory_items", ["run_id"], unique=False)

    op.create_table(
        "leaderboard_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name_snapshot", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("floors_cleared", sa.Integer(), server_default="0", nullable=False),
        sa.Column("class_id", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("score >= 0", name=op.f("ck_leaderboard_entries_score_non_negative")),
        sa.CheckConstraint("floors_cleared >= 0", name=op.f("ck_leaderboard_entries_floors_cleared_non_negative")),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE", name=op.f("fk_leaderboard_entries_player_id_players")),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE", name=op.f("fk_leaderboard_entries_run_id_runs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leaderboard_entries")),
        sa.UniqueConstraint("run_id", name=op.f("uq_leaderboard_entries_run_id")),
    )
    op.create_index(op.f("ix_leaderboard_entries_created_at"), "leaderboard_entries", ["created_at"], unique=False)
    op.create_index(op.f("ix_leaderboard_entries_score"), "leaderboard_entries", ["score"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leaderboard_entries_score"), table_name="leaderboard_entries")
    op.drop_index(op.f("ix_leaderboard_entries_created_at"), table_name="leaderboard_entries")
    op.drop_table("leaderboard_entries")

    op.drop_index(op.f("ix_inventory_items_run_id"), table_name="inventory_items")
    op.drop_table("inventory_items")

    op.drop_index(op.f("ix_encounters_run_id"), table_name="encounters")
    op.drop_table("encounters")

    op.drop_index(op.f("ix_runs_status"), table_name="runs")
    op.drop_index(op.f("ix_runs_started_at"), table_name="runs")
    op.drop_index(op.f("ix_runs_save_slot_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_player_id"), table_name="runs")
    op.drop_table("runs")

    op.drop_index(op.f("ix_save_slots_player_id"), table_name="save_slots")
    op.drop_table("save_slots")

    op.drop_table("players")
    op.drop_table("healthcheck_records")
    op.drop_table("asset_manifest")
