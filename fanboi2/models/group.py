from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String

from ._base import Base


class Group(Base):
    """Model class for group-based ACL."""

    __tablename__ = 'group'
    __table_args__ = (UniqueConstraint('name'),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
