"""add status column to board

Revision ID: bfbd6a58775c
Revises: 28d3c8870c89
Create Date: 2016-10-28 10:28:22.055645

"""

# revision identifiers, used by Alembic.
revision = 'bfbd6a58775c'
down_revision = '28d3c8870c89'

from alembic import op
from sqlalchemy import sql
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


def _add_status_column(table_name, column):
    op.add_column(table_name, sa.Column('status', column))
    table = sql.table(table_name, sql.column('status'))
    op.execute(table.update().values(status='open'))
    op.alter_column(table_name, 'status', nullable=False)


def upgrade():
    board_status = sa.Enum(
        'open',
        'restricted',
        'locked',
        'archived',
        name='board_status')

    # Workaround Alembic couldn't automatically create types in add_column
    # See https://bitbucket.org/zzzeek/alembic/issues/89/
    bind = op.get_bind()
    impl = board_status.dialect_impl(bind.dialect)
    impl.create(bind, checkfirst=True)

    _add_status_column('board', board_status)
    _add_status_column('board_history', board_status)


def downgrade():
    op.drop_column('board_history', 'status')
    op.drop_column('board', 'status')
    ENUM(name='board_status').drop(op.get_bind(), checkfirst=True)
