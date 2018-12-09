import re

from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import desc, func, select
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime, Unicode

from ._base import Base, Versioned
from ._type import TopicStatusEnum
from .post import Post
from .topic_meta import TopicMeta


class Topic(Versioned, Base):
    """Model class for topic. This model only holds topic metadata such as
    title or its associated board. The actual content of a topic belongs
    to :class:`Post`.
    """

    __tablename__ = "topic"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    board_id = Column(Integer, ForeignKey("board.id"), nullable=False)
    title = Column(Unicode(255), nullable=False)
    status = Column(TopicStatusEnum, default="open", nullable=False)

    board = relationship(
        "Board",
        backref=backref(
            "topics",
            lazy="dynamic",
            cascade="all,delete",
            order_by=desc(
                func.coalesce(
                    select([TopicMeta.bumped_at])
                    .where(TopicMeta.topic_id == id)
                    .as_scalar(),
                    created_at,
                )
            ),
        ),
    )

    QUERY = (
        ("single_post", re.compile(r"^(\d+)$")),
        ("ranged_posts", re.compile(r"^(\d+)?\-(\d+)?$")),
        ("recent_posts", re.compile(r"^l(\d+)$")),
        ("recent_posts", re.compile(r"^recent$")),
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
        return (
            self.posts.order_by(False)
            .order_by(desc(Post.number))
            .limit(count)
            .all()[::-1]
        )
