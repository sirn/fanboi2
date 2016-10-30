from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, DateTime, String, Text, Unicode
from ._base import Base, Versioned


INTERNAL_PAGES = (
    ('global_css', 'none'),
    ('global_appendix', 'markdown'),
)


class Page(Versioned, Base):
    """Model class for pages. This model is a basis for user-accessible
    content that are not part of the board itself, including individual pages,
    custom CSS or board guidelines.
    """

    __tablename__ = 'page'
    __table_args__ = (UniqueConstraint('namespace', 'slug'),)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    namespace = Column(String, nullable=False, default='public')
    title = Column(Unicode, nullable=False)
    slug = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    formatter = Column(String, nullable=False, default='markdown')
