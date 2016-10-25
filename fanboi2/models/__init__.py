from sqlalchemy import event
from sqlalchemy.sql import desc, func, select
from ._base import DBSession, Base, JsonType
from ._identity import Identity
from ._redis_proxy import RedisProxy
from ._versioned import make_versioned
from .board import Board
from .topic import Topic
from .topic_meta import TopicMeta
from .post import Post


_MODELS = {
    'board': Board,
    'topic': Topic,
    'topic_meta': TopicMeta,
    'post': Post,
}

def serialize_model(type_):
    return _MODELS.get(type_)


redis_conn = RedisProxy()
identity = Identity(redis=redis_conn)
make_versioned(DBSession)


@event.listens_for(DBSession, 'before_flush')
def _create_topic_meta(session, context, instances):
    """Assign a new topic meta to a topic on creation."""
    for topic in filter(lambda m: isinstance(m, Topic), session.new):
        if topic.meta is None:
            topic.meta = TopicMeta(post_count=0)


@event.listens_for(DBSession, 'before_flush')
def _update_topic_meta_states(session, context, instance):
    """Update topic metadata and related states when new posts are made."""
    for post in filter(lambda m: isinstance(m, Post), session.new):
        topic = post.topic
        board = topic.board
        if topic in session.new:
            topic_meta = topic.meta
        else:
            topic_meta = session.query(TopicMeta).\
                         filter_by(topic=topic).\
                         with_for_update().\
                         one()

        topic_meta.post_count = post.number = topic_meta.post_count + 1
        topic_meta.posted_at = post.created_at or func.now()
        if post.bumped is None or post.bumped:
            topic_meta.bumped_at = topic_meta.posted_at

        if topic.status == 'open' and \
           topic_meta.post_count >= board.settings['max_posts']:
            topic.status = 'archived'

        session.add(topic_meta)
        session.add(topic)
        session.add(post)
