"""create user tables

Revision ID: 11d55f8444d4
Revises: 05314e264e76
Create Date: 2018-05-01 10:28:26.041813
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET


revision = '11d55f8444d4'
down_revision = '05314e264e76'


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('logged_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('encrypted_password', sa.String(), nullable=False),
        sa.Column('deactivated', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.Index(None, 'deactivated'),
        sa.ForeignKeyConstraint(['parent_id'], ['user.id']))

    op.create_table(
        'user_session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('ip_address', INET(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']))

    op.create_table(
        'user_group',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.UniqueConstraint('user_id', 'group_id'))

    op.create_table(
        'group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'))


def downgrade():
    op.drop_table('group')
    op.drop_table('user_group')
    op.drop_table('user_session')
    op.drop_table('user')
