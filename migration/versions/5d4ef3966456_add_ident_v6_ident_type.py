"""add ident_v6 ident type

Revision ID: 5d4ef3966456
Revises: 06000cefb0bb
Create Date: 2020-03-30 19:29:21.471805
"""
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


revision = "5d4ef3966456"
down_revision = "06000cefb0bb"


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
        "ident_type",
        ("none", "ident", "ident_v6", "ident_admin"),
        (
            ("user", "ident_type"),
            ("post", "ident_type"),
            ("post_history", "ident_type"),
        ),
    )


def downgrade():
    alter_enum(
        "ident_type",
        ("none", "ident", "ident_admin"),
        (
            ("user", "ident_type"),
            ("post", "ident_type"),
            ("post_history", "ident_type"),
        ),
    )
