from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from ._versioned import make_versioned_class


class BaseModel(object):
    """Primary mixin that provides common behavior for SQLAlchemy models."""

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


metadata = MetaData(naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

Base = declarative_base(metadata=metadata, cls=BaseModel)
Versioned = make_versioned_class()
