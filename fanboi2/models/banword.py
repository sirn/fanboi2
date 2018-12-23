from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String

from ._base import Base


class Banword(Base):
    """Model class for banwords."""

    __tablename__ = "banword"

    id = Column(Integer, primary_key=True)
    scope = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expr = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
