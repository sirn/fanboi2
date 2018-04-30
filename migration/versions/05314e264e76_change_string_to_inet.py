"""change string to inet

Revision ID: 05314e264e76
Revises: 0df7bc63ddf1
Create Date: 2018-04-30 18:23:00.343146
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET


revision = '05314e264e76'
down_revision = '0df7bc63ddf1'


def _convert_string_inet(table_name, column_name):
    op.alter_column(
        table_name,
        column_name,
        type_=INET(),
        postgresql_using='{}::inet'.format(column_name))


def _convert_inet_string(table_name, column_name):
    op.alter_column(
        table_name,
        column_name,
        type_=sa.String())


def upgrade():
    _convert_string_inet('post', 'ip_address')
    _convert_string_inet('post_history', 'ip_address')
    op.create_index(None, 'post', ['ip_address'])


def downgrade():
    _convert_inet_string('post', 'ip_address')
    _convert_inet_string('post_history', 'ip_address')
    op.drop_index(None, 'post', ['ip_address'])
