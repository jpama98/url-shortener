"""init

Revision ID: 0001_init
Revises: 
Create Date: 2025-12-15

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "short_urls",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("target_url", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_short_urls_code", "short_urls", ["code"], unique=True)
    op.create_index("ix_short_urls_owner_id", "short_urls", ["owner_id"], unique=False)

    op.create_table(
        "click_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("link_id", sa.Uuid(), sa.ForeignKey("short_urls.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("referer", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_click_events_link_id", "click_events", ["link_id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_click_events_link_id", table_name="click_events")
    op.drop_table("click_events")
    op.drop_index("ix_short_urls_owner_id", table_name="short_urls")
    op.drop_index("ix_short_urls_code", table_name="short_urls")
    op.drop_table("short_urls")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
