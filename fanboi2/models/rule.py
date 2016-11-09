from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func, desc, and_, or_
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, DateTime, Boolean, String, Unicode
from ._base import Base


class Rule(Base):
    """Model class that provides an IP rule."""

    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ip_address = Column(INET, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    active_until = Column(DateTime(timezone=True))
    description = Column(Unicode)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'base',
    }

    @classmethod
    def listed(cls, ip_address):
        return and_(
            cls.active == True,
            cls.ip_address.op('>>=')(ip_address),
            or_(cls.active_until == None,
                cls.active_until >= func.now()))
