"""Create initial tables

Revision ID: 38f5ad30fe6f
Revises: None
Create Date: 2013-01-11 06:13:22.487819

"""

# revision identifiers, used by Alembic.
revision = '38f5ad30fe6f'
down_revision = None

from alembic import op
from fanboi2.models import JsonType
import sqlalchemy as sa


def upgrade():
    op.create_table('board',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('slug', sa.String(length=64), nullable=False),
        sa.Column('title', sa.Unicode(length=255), nullable=False),
        sa.Column('settings', JsonType(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table('topic',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('board_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=255), nullable=False),
        sa.ForeignKeyConstraint(['board_id'], ['board.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('ident', sa.String(length=32), nullable=True),
        sa.Column('body', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('post')
    op.drop_table('topic')
    op.drop_table('board')
