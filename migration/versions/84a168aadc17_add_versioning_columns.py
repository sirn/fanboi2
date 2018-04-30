"""add versioning columns

Revision ID: 84a168aadc17
Revises: c71cae24d11
Create Date: 2016-10-24 11:56:06.244550
"""
from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


revision = '84a168aadc17'
down_revision = 'c71cae24d111'


def _add_version_column(table_name):
    op.add_column(table_name, sa.Column('version', sa.Integer))
    table = sql.table(table_name, sql.column('version'))
    op.execute(table.update().values(version=1))
    op.alter_column(table_name, 'version', nullable=False)


def upgrade():
    _add_version_column('board')
    _add_version_column('topic')
    _add_version_column('post')


def downgrade():
    op.drop_column('board', 'version')
    op.drop_column('topic', 'version')
    op.drop_column('post', 'version')
