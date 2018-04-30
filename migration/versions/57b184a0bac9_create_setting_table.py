"""create setting table

Revision ID: 57b184a0bac9
Revises: 6af2b8c6dc3a
Create Date: 2018-04-11 17:30:37.793660
"""
from alembic import op
import sqlalchemy as sa


revision = '57b184a0bac9'
down_revision = '6af2b8c6dc3a'


def upgrade():
    op.create_table(
        'setting',
        sa.Column('key', sa.String(), nullable=False, primary_key=True),
        sa.Column('value', sa.JSON()),
        sa.Column('version', sa.Integer(), nullable=False))

    op.create_table(
        'setting_history',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.JSON()),
        sa.Column('version',
                  sa.Integer(),
                  nullable=False,
                  autoincrement=False),
        sa.Column('change_type', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('key', 'version'))


def downgrade():
    op.drop_table('setting')
    op.drop_table('setting_history')
