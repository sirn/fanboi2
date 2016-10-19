import json
import re
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text
from sqlalchemy.sql.type_api import TypeDecorator
from zope.sqlalchemy import ZopeTransactionExtension
from ._versioned import make_versioned_class


RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')


class JsonType(TypeDecorator):
    """Serializable field for storing data as JSON text. If the field is
    ``NULL`` in the database, a default value of empty :type:`dict` is
    returned on retrieval.
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if not value:
            return {}
        return json.loads(value)


class BaseModel(object):
    """Primary mixin that provides common fields for SQLAlchemy models."""

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def __tablename__(self):
        name = RE_FIRST_CAP.sub(r'\1_\2', self.__name__)
        return RE_ALL_CAP.sub(r'\1_\2', name).lower()

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


Versioned = make_versioned_class()


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(cls=BaseModel)
