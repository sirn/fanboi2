from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer, String, Unicode

from ._base import Base


class Ban(Base):
    """Model class that provides an IP ban."""

    __tablename__ = "ban"

    id = Column(Integer, primary_key=True)
    scope = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ip_address = Column(INET, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    active_until = Column(DateTime(timezone=True))
    description = Column(Unicode)

    @property
    def duration(self):
        """Returns the duration of this ban in days."""
        if not self.active_until:
            return 0
        secs = (self.active_until - self.created_at).total_seconds()
        return round(secs / 86400)
