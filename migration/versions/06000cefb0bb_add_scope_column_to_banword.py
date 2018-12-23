"""add scope column to banword

Revision ID: 06000cefb0bb
Revises: 47c309ddc2b9
Create Date: 2018-12-23 11:25:44.866557
"""
from alembic import op
import sqlalchemy as sa


revision = "06000cefb0bb"
down_revision = "47c309ddc2b9"


def upgrade():
    op.add_column("banword", sa.Column("scope", sa.String))


def downgrade():
    op.drop_column("banword", "scope")
