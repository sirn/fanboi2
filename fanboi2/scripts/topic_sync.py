import os
import sys
import transaction
import sqlalchemy as sa
from fanboi2.models import DBSession, TopicMeta, Post
from pyramid.paster import bootstrap


def main(argv=sys.argv):
    if not len(argv) >= 2:
        sys.stderr.write("Usage: %s config\n" % os.path.basename(argv[0]))
        sys.stderr.write("Configuration file not present.\n")
        sys.exit(1)

    bootstrap(argv[1])

    query = TopicMeta.__table__.update().\
            values(bumped_at=sa.select([Post.created_at]).\
                   where(Post.topic_id == TopicMeta.topic_id).\
                   where(Post.bumped).\
                   order_by(sa.desc(Post.created_at)).\
                   limit(1)).\
                returning(TopicMeta.topic_id,
                          TopicMeta.bumped_at)

    with transaction.manager:
        for topic_id, bumped_at in DBSession.execute(query):
            print("Topic %s set bumped_at to %s" % (topic_id, bumped_at))
