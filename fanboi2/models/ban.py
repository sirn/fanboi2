from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func, and_, or_
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

    @classmethod
    def listed(cls, ip_address, scopes=None):
        scope_q = cls.scope == None  # noqa: E712
        if scopes is not None:
            scope_q = or_(scope_q, cls.scope.in_(scopes))
        return and_(
            scope_q,
            cls.active == True,  # noqa: E712
            cls.ip_address.op(">>=")(ip_address),
            or_(cls.active_until == None, cls.active_until >= func.now()),  # noqa: E712
        )

    @property
    def duration(self):
        """Returns the duration of this ban in days."""
        if not self.active_until:
            return 0
        secs = (self.active_until - self.created_at).total_seconds()
        return round(secs / 86400)
