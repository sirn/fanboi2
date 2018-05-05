from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, DateTime, String
from sqlalchemy.dialects.postgresql import INET
from ._base import Base


class UserSession(Base):
    """Model class that provides a user session for managing logins."""

    __tablename__ = 'user_session'
    __table_args__ = (UniqueConstraint('token'),)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_seen_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String, nullable=False)
    ip_address = Column(INET, nullable=False)

    user = relationship('User',
                        backref=backref(
                            'sessions',
                            lazy='dynamic',
                            cascade='all,delete',
                            order_by='desc(UserSession.created_at)'))
