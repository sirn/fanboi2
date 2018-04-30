from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, JSON

from ._base import Base, Versioned


DEFAULT_SETTINGS = {
    'app.time_zone': 'UTC',
    'app.ident_size': 10,
}


class Setting(Versioned, Base):
    """Model class for various site settings."""

    __tablename__ = 'setting'

    key = Column(String, nullable=False, primary_key=True)
    value = Column(JSON)
