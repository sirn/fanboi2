"""merge rule tables

Revision ID: e7cd2e4753bf
Revises: 199110fb8ce5
Create Date: 2018-06-23 19:16:19.893491
"""
from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


revision = "e7cd2e4753bf"
down_revision = "199110fb8ce5"


def upgrade():
    rule_table = sql.table("rule", sa.column("type"))
    op.execute(rule_table.delete().where(rule_table.c.type != "ban"))
    op.drop_column("rule", "type")
    op.rename_table("rule", "ban")
    op.drop_table("rule_ban")
    op.drop_constraint("pk_rule", "ban")
    op.create_primary_key("pk_ban", "ban", ["id"])


def downgrade():
    op.rename_table("ban", "rule")
    op.drop_constraint("pk_ban", "rule")
    op.create_primary_key("pk_rule", "rule", ["id"])

    op.add_column("rule", sa.Column("type", sa.String()))
    rule_table = sql.table("rule", sa.column("id"), sa.column("type"))
    op.execute(rule_table.update().values(type="ban"))

    op.create_table(
        "rule_ban",
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["rule_id"], ["rule.id"]),
        sa.PrimaryKeyConstraint("rule_id"),
    )

    rule_ban_table = sql.table("rule_ban", sa.column("rule_id"))
    op.execute(
        rule_ban_table.insert().from_select(
            [rule_ban_table.c.rule_id], sa.select([rule_table.c.id])
        )
    )
