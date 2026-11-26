"""Add debate_events table for Step 12.5 live agent debate streaming.

Revision ID: 002_debate_events
Revises: 001_initial_schema
Create Date: 2026-11-26 22:12:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_debate_events"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "debate_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(length=36),
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("schema_version", sa.String(length=20), nullable=False, server_default="1.0.0"),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("agent_role", sa.String(length=64), nullable=True),
        sa.Column("target_agent_role", sa.String(length=64), nullable=True),
        sa.Column("round_number", sa.Integer(), nullable=True),
        sa.Column("claim_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="info"),
        sa.Column("evidence_references", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "sequence_number", name="uq_debate_events_session_seq"),
    )
    op.create_index("ix_debate_events_session_id", "debate_events", ["session_id"])
    op.create_index("ix_debate_events_event_type", "debate_events", ["event_type"])
    op.create_index("ix_debate_events_session_seq", "debate_events", ["session_id", "sequence_number"])


def downgrade() -> None:
    op.drop_index("ix_debate_events_session_seq", table_name="debate_events")
    op.drop_index("ix_debate_events_event_type", table_name="debate_events")
    op.drop_index("ix_debate_events_session_id", table_name="debate_events")
    op.drop_table("debate_events")

