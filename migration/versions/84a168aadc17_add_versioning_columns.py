"""add versioning columns

Revision ID: 84a168aadc17
Revises: c71cae24d1
Create Date: 2016-10-24 11:56:06.244550

"""

# revision identifiers, used by Alembic.
revision = '84a168aadc17'
down_revision = 'c71cae24d1'

from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


def _add_version_column(table):
    op.add_column(table, sa.Column('version', sa.Integer))
    version_column = sql.table(table, sql.column('version'))
    op.execute(version_column.update().values(version=1))
    op.alter_column(table, 'version', nullable=False)


def upgrade():
    _add_version_column('board')
    _add_version_column('topic')
    _add_version_column('post')


def downgrade():
    op.drop_column('board', 'version')
    op.drop_column('topic', 'version')
    op.drop_column('post', 'version')
