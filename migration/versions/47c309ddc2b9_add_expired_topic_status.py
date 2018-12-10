"""add expired topic status

Revision ID: 47c309ddc2b9
Revises: ef4ade81032b
Create Date: 2018-12-05 13:09:43.389842
"""
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


revision = "47c309ddc2b9"
down_revision = "ef4ade81032b"


def alter_enum(enum_name, enum_value, fields=None):
    op.execute("ALTER TYPE %s RENAME TO %s_1" % (enum_name, enum_name))

    new_enum = sa.Enum(*enum_value, name=enum_name)
    new_enum.create(op.get_bind(), checkfirst=True)
    if fields:
        for table, column in fields:
            op.alter_column(
                table,
                column,
                type_=new_enum,
                postgresql_using="%s::text::%s" % (column, enum_name),
            )

    ENUM(name="%s_1" % enum_name).drop(op.get_bind(), checkfirst=True)


def upgrade():
    alter_enum(
        "topic_status",
        ("open", "locked", "archived", "expired"),
        (("topic", "status"), ("topic_history", "status")),
    )


def downgrade():
    alter_enum(
        "topic_status",
        ("open", "locked", "archived"),
        (("topic", "status"), ("topic_history", "status")),
    )
