from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column, Table, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, DateTime, String, Boolean

from ._base import Base
from ._type import IdentTypeEnum


user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("group_id", Integer, ForeignKey("group.id")),
)


class User(Base):
    """Model class that provides a user."""

    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("username"),)

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    parent_id = Column(Integer, ForeignKey("user.id"))
    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    deactivated = Column(Boolean, nullable=False, index=True, default=False)

    ident = Column(String, nullable=False)
    ident_type = Column(IdentTypeEnum, default="ident", nullable=False)
    name = Column(String, nullable=False)

    parent = relationship(
        "User",
        remote_side=[id],
        backref=backref(
            "children", lazy="dynamic", cascade="all,delete", order_by="User.id"
        ),
    )

    groups = relationship(
        "Group",
        secondary="user_group",
        order_by="Group.name",
        backref=backref("users", lazy="dynamic", order_by="User.id"),
    )
