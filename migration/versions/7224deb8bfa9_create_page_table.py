"""create page table

Revision ID: 7224deb8bfa9
Revises: a6f20e3c63c2
Create Date: 2016-10-30 10:13:38.772224

"""

# revision identifiers, used by Alembic.
revision = '7224deb8bfa9'
down_revision = 'a6f20e3c63c2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('namespace', sa.String(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('formatter', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('namespace', 'slug'),
    )
    op.create_table('page_history',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('namespace', sa.String(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('formatter', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('change_type', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', 'version'),
    )


def downgrade():
    op.drop_table('page_history')
    op.drop_table('page')
