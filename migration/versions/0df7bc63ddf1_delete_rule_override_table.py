"""delete rule override table

Revision ID: 0df7bc63ddf1
Revises: 53ab606666d3
Create Date: 2018-04-19 18:48:12.363228
"""
from alembic import op
import sqlalchemy as sa


revision = '0df7bc63ddf1'
down_revision = '53ab606666d3'


def upgrade():
    op.drop_table('rule_override')


def downgrade():
    op.create_table(
        'rule_override',
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('override', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['rule.id']),
        sa.PrimaryKeyConstraint('rule_id'))
