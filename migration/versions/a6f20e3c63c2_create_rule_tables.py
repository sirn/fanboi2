"""create rule tables

Revision ID: a6f20e3c63c2
Revises: bfbd6a58775c
Create Date: 2016-10-29 09:40:09.935442
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET


revision = 'a6f20e3c63c2'
down_revision = 'bfbd6a58775c'


def upgrade():
    op.create_table(
        'rule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', INET(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('active_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('id'))

    op.create_table(
        'rule_ban',
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['rule.id']),
        sa.PrimaryKeyConstraint('rule_id'))

    op.create_table(
        'rule_override',
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('override', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['rule.id']),
        sa.PrimaryKeyConstraint('rule_id'))


def downgrade():
    op.drop_table('rule_override')
    op.drop_table('rule_ban')
    op.drop_table('rule')
