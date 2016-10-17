import re
from sqlalchemy import event
from sqlalchemy.orm import backref, column_property, relationship
from sqlalchemy.sql import desc, func, select
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Enum, Unicode
from ._base import Base, DBSession
from .post import Post


class Topic(Base):
    """Model class for topic. This model only holds topic metadata such as
    title or its associated board. The actual content of a topic belongs
    to :class:`Post`.
    """

    board_id = Column(Integer, ForeignKey('board.id'), nullable=False)
    title = Column(Unicode(255), nullable=False)
    status = Column(Enum('open', 'locked', 'archived', name='topic_status'),
                    default='open',
                    nullable=False)
    board = relationship('Board',
                         backref=backref('topics',
                                         lazy='dynamic',
                                         order_by="desc(func.coalesce("
                                                  "Topic.bumped_at,"
                                                  "Topic.created_at))"))

    QUERY = (
        ("single_post", re.compile("^(\d+)$")),
        ("ranged_posts", re.compile("^(\d+)?\-(\d+)?$")),
        ("recent_posts", re.compile("^l(\d+)$")),
        ("recent_posts", re.compile("^recent$")),
    )

    def scoped_posts(self, query=None):
        """Return single post or multiple posts according to `query`. If
        `query` is not given, this method is an equivalent of calling
        :attr:`posts` directly. This method always returns an iterator.

        Single numeric (e.g. "253")
          Returns a single post that matches the number. For example if
          "253" is given, then an iterator containing post number "253" is
          returned.

        Ranged query (e.g. "100-150")
          Returns all posts within range. If start number is missing ("-150")
          or end number is missing ("100-") then the first post and last post
          are automatically assumed.

        Recent query (e.g. "l30", "recent")
          Returns the n last posts where n is the number after "l" letter.
          If named "recent" is given, then a default value of last 20 posts
          is used instead.
        """
        if query is None:
            return self.posts.all()
        else:
            for handler, matcher in self.QUERY:
                match = matcher.match(str(query))
                if match:
                    fn = getattr(self, handler)
                    return fn(*match.groups())
        return []

    def single_post(self, number=None):
        """Returns an iterator that contains a single post that matches
        `number`. If post with such number could not be found, an empty
        iterator is returned.
        """
        if not number:
            number = -1
        return self.posts.filter_by(number=int(number)).all()

    def ranged_posts(self, start=None, end=None):
        """Returns a range of post between `start` and `end`. When `start` or
        `end` is empty, the first and last posts are assumed respectively.
        """
        if start is None:
            start = 1
        if end is None:
            query = Post.number >= start
        else:
            query = Post.number.between(start, end)
        return self.posts.filter(query).all()

    def recent_posts(self, count=30):
        """Returns recent `count` number of posts associated with this topic.
        Defaults to 30 posts if `count` is not given.
        """
        return self.posts.order_by(False).\
            order_by(desc(Post.number)).\
            limit(count).all()[::-1]


@event.listens_for(DBSession, 'before_flush')
def update_topic_status(session, context, instances):
    for obj in filter(lambda obj: isinstance(obj, Post), session.new):
        topic = obj.topic
        if topic.post_count is not None and \
                topic.status == 'open' and \
                topic.post_count >= (topic.board.settings['max_posts'] - 1):
            topic.status = 'archived'
            session.add(topic)


Topic.post_count = column_property(
    select([func.coalesce(func.max(Post.number), 0)]).
    where(Post.topic_id == Topic.id)
)


Topic.posted_at = column_property(
    select([Post.created_at]).
        where(Post.topic_id == Topic.id).
        order_by(desc(Post.created_at)).
        limit(1)
)


Topic.bumped_at = column_property(
    select([Post.created_at]).
        where(Post.topic_id == Topic.id).
        where(Post.bumped).
        order_by(desc(Post.created_at)).
        limit(1)
)
