"""create versioning tables

Revision ID: 0d0f281cc4ec
Revises: 84a168aadc17
Create Date: 2016-10-24 12:23:08.537936

"""

# revision identifiers, used by Alembic.
revision = '0d0f281cc4ec'
down_revision = '84a168aadc17'

from alembic import op
from fanboi2.models import JsonType
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


def upgrade():
    op.create_table('board_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('slug', sa.String(length=64), nullable=False),
        sa.Column('title', sa.Unicode(length=255), nullable=False),
        sa.Column('agreements', sa.Text, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('settings', JsonType(), nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('change_type', sa.String),
        sa.Column('changed_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id', 'version', name='pk_board'),
    )
    op.create_table('topic_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=255), nullable=False),
        sa.Column('status',
                  ENUM('open', 'locked', 'archived',
                       name='topic_status',
                       create_type=False),
                  nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('change_type', sa.String),
        sa.Column('changed_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id', 'version', name='pk_topic')
    )
    op.create_table('post_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('ident', sa.String(length=32), nullable=True),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('bumped', sa.Boolean(), nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('change_type', sa.String),
        sa.Column('changed_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id', 'version', name='pk_post')
    )


def downgrade():
    op.drop_table('post_history')
    op.drop_table('topic_history')
    op.drop_table('board_history')
