from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Integer, String, Text, Unicode, JSON

from ._base import Base, Versioned
from ._type import BoardStatusEnum


DEFAULT_BOARD_CONFIG = {
    "name": "Nameless Fanboi",
    "use_ident": True,
    "max_posts": 1000,
    "post_delay": 10,
    "expire_duration": 0,
}


class Board(Versioned, Base):
    """Model class for board. This model serve as a category to topic and
    also holds settings regarding how posts are created and displayed. It
    should always be accessed using :attr:`slug`.
    """

    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    slug = Column(String(64), unique=True, nullable=False)
    title = Column(Unicode(255), nullable=False)
    _settings = Column("settings", JSON, nullable=False, default={})
    agreements = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(BoardStatusEnum, default="open", nullable=False)

    def get_settings(self):
        if self._settings is None:
            return DEFAULT_BOARD_CONFIG
        settings = DEFAULT_BOARD_CONFIG.copy()
        settings.update(self._settings)
        return settings

    def set_settings(self, value):
        self._settings = value

    @declared_attr
    def settings(self):
        return synonym(
            "_settings", descriptor=property(self.get_settings, self.set_settings)
        )
