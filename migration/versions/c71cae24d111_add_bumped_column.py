"""add bumped column

Revision ID: c71cae24d111
Revises: 38f5ad30fe6f
Create Date: 2013-12-05 12:01:35.668738
"""
from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


revision = 'c71cae24d111'
down_revision = '38f5ad30fe6f'


def upgrade():
    op.add_column('post', sa.Column('bumped', sa.Boolean))
    table = sql.table('post', sql.column('bumped'))
    op.execute(table.update().values(bumped=True))
    op.alter_column('post', 'bumped', nullable=False)
    op.create_index(None, 'post', ['bumped'])


def downgrade():
    op.drop_column('post', 'bumped')
