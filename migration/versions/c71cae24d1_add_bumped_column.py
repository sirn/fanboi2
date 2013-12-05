"""add bumped column

Revision ID: c71cae24d1
Revises: 38f5ad30fe6f
Create Date: 2013-12-05 12:01:35.668738

"""

# revision identifiers, used by Alembic.
revision = 'c71cae24d1'
down_revision = '38f5ad30fe6f'

from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


def upgrade():
    op.add_column('post', sa.Column('bumped', sa.Boolean))
    post_column = sql.table('post', sql.column('bumped'))
    op.execute(post_column.update().values(bumped=True))
    op.alter_column('post', 'bumped', nullable=False)
    op.create_index('ix_post_bumped', 'post', ['bumped'])


def downgrade():
    op.drop_column('post', 'bumped')
