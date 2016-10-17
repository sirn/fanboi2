from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import synonym
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Text, Unicode
from ._base import Base, JsonType


DEFAULT_BOARD_CONFIG = {
    'name': 'Nameless Fanboi',
    'use_ident': True,
    'max_posts': 1000,
    'post_delay': 10,
}


class Board(Base):
    """Model class for board. This model serve as a category to topic and
    also holds settings regarding how posts are created and displayed. It
    should always be accessed using :attr:`slug`.
    """

    slug = Column(String(64), unique=True, nullable=False)
    title = Column(Unicode(255), nullable=False)
    _settings = Column('settings', JsonType, nullable=False, default={})
    agreements = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    def get_settings(self):
        settings = DEFAULT_BOARD_CONFIG.copy()
        settings.update(self._settings)
        return settings

    def set_settings(self, value):
        self._settings = value

    @declared_attr
    def settings(cls):
        return synonym('_settings', descriptor=property(cls.get_settings,
                                                        cls.set_settings))
