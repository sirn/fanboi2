"""add ident columns

Revision ID: 199110fb8ce5
Revises: 11d55f8444d4
Create Date: 2018-05-12 20:46:43.940606
"""
import string
import random

from alembic import op
from sqlalchemy import sql
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


revision = '199110fb8ce5'
down_revision = '11d55f8444d4'


STRINGS = string.ascii_letters + string.digits + "+/."


def _add_ident_type_column(table_name, column):
    op.add_column(table_name, sa.Column('ident_type', column))
    table = sql.table(
        table_name,
        sql.column('ident'),
        sql.column('ident_type'))
    op.execute(
        table.update().
        values(ident=None, ident_type='none').
        where(sql.or_(
            table.c.ident == None,  # noqa: E711
            table.c.ident == '')))
    op.execute(
        table.update().
        values(ident_type='ident').
        where(table.c.ident_type == None))  # noqa: E711
    op.alter_column(table_name, 'ident_type', nullable=False)


def upgrade():
    ident_type = sa.Enum(
        'none',
        'ident',
        'ident_admin',
        name='ident_type')

    # Workaround Alembic couldn't automatically create types in add_column
    # See https://bitbucket.org/zzzeek/alembic/issues/89/
    bind = op.get_bind()
    impl = ident_type.dialect_impl(bind.dialect)
    impl.create(bind, checkfirst=True)

    _add_ident_type_column('post', ident_type)
    _add_ident_type_column('post_history', ident_type)

    op.add_column('user', sa.Column('ident', sa.String))
    op.add_column('user', sa.Column('ident_type', ident_type))
    op.add_column('user', sa.Column('name', sa.String))
    table = sql.table(
        'user',
        sa.column('ident'),
        sa.column('ident_type'),
        sa.column('name'))
    op.execute(table.update().values(
        ident=''.join(random.choice(STRINGS) for x in range(10)),
        ident_type='ident_admin',
        name='Nameless Moderator'))
    op.alter_column('user', sa.Column('ident', nullable=False))
    op.alter_column('user', sa.Column('ident_type', nullable=False))
    op.alter_column('user', sa.Column('name', nullable=False))


def downgrade():
    op.drop_column('user', 'name')
    op.drop_column('user', 'ident_type')
    op.drop_column('user', 'ident')
    op.drop_column('post_history', 'ident_type')
    op.drop_column('post', 'ident_type')
    ENUM(name='ident_type').drop(op.get_bind(), checkfirst=True)
