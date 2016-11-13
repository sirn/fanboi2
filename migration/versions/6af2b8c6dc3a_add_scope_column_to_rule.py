"""add scope column to rule

Revision ID: 6af2b8c6dc3a
Revises: 7224deb8bfa9
Create Date: 2016-11-12 19:55:55.185797

"""

# revision identifiers, used by Alembic.
revision = '6af2b8c6dc3a'
down_revision = '7224deb8bfa9'

from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


def upgrade():
    op.add_column('rule', sa.Column('scope', sa.String))


def downgrade():
    op.drop_column('rule', 'scope')
