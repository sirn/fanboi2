"""change jsontype to json

Revision ID: 53ab606666d3
Revises: 57b184a0bac9
Create Date: 2018-04-12 21:22:47.384783
"""
from alembic import op
import sqlalchemy as sa


revision = '53ab606666d3'
down_revision = '57b184a0bac9'


def _convert_jsontype_json(table_name, column_name):
    op.alter_column(
        table_name,
        column_name,
        type_=sa.JSON(),
        postgresql_using='{}::json'.format(column_name))


def _convert_json_jsontype(table_name, column_name):
    op.alter_column(
        table_name,
        column_name,
        type_=sa.Text())


def upgrade():
    _convert_jsontype_json('board', 'settings')
    _convert_jsontype_json('board_history', 'settings')
    _convert_jsontype_json('rule_override', 'override')


def downgrade():
    _convert_json_jsontype('board', 'settings')
    _convert_json_jsontype('board_history', 'settings')
    _convert_json_jsontype('rule_override', 'override')
