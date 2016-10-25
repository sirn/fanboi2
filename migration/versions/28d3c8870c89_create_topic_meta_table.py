"""create topic meta table

Revision ID: 28d3c8870c89
Revises: 0d0f281cc4ec
Create Date: 2016-10-25 11:52:14.806880

"""

# revision identifiers, used by Alembic.
revision = '28d3c8870c89'
down_revision = '0d0f281cc4ec'

from alembic import op
from sqlalchemy import sql
import sqlalchemy as sa


def upgrade():
    op.create_table('topic_meta',
        sa.Column('topic_id',
                  sa.Integer(),
                  autoincrement=False,
                  nullable=False),
        sa.Column('post_count', sa.Integer(), nullable=False),
        sa.Column('posted_at', sa.DateTime(timezone=True)),
        sa.Column('bumped_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
        sa.PrimaryKeyConstraint('topic_id'),
    )

    topic_meta_table = sql.table(
        'topic_meta',
        sql.column('topic_id'),
        sql.column('post_count'),
        sql.column('posted_at'),
        sql.column('bumped_at'))

    topic_table = sql.table(
        'topic',
        sql.column('id'))

    post_table = sql.table(
        'post',
        sql.column('created_at'),
        sql.column('topic_id'),
        sql.column('number'),
        sql.column('bumped'))

    op.execute(
        topic_meta_table.
        insert().
        from_select(
            [
                topic_meta_table.c.topic_id,
                topic_meta_table.c.post_count,
                topic_meta_table.c.posted_at,
                topic_meta_table.c.bumped_at
            ],
            sa.select(
                [
                    topic_table.c.id,
                    sa.select([
                            sa.func.coalesce(
                                sa.func.max(post_table.c.number),
                                0).
                            label('post_count')]).
                        where(post_table.c.topic_id == topic_table.c.id).
                        label('post_count_q'),
                    sa.select([post_table.c.created_at.label('posted_at')]).
                        where(post_table.c.topic_id == topic_table.c.id).
                        order_by(sa.desc(post_table.c.created_at)).
                        limit(1).
                        label('posted_at_q'),
                    sa.select([post_table.c.created_at.label('bumped_at')]).
                        where(post_table.c.topic_id == topic_table.c.id).
                        where(post_table.c.bumped).
                        order_by(sa.desc(post_table.c.created_at)).
                        limit(1).
                        label('bumped_at_q'),
                ]
            )
        )
    )


def downgrade():
    op.drop_table('topic_meta')
