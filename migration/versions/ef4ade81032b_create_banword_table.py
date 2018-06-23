"""create banword table

Revision ID: ef4ade81032b
Revises: e7cd2e4753bf
Create Date: 2018-06-23 20:37:45.525014
"""
from alembic import op
import sqlalchemy as sa


revision = "ef4ade81032b"
down_revision = "e7cd2e4753bf"


def upgrade():
    op.create_table(
        "banword",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expression", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("banword")
