import json
import re
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.sqltypes import Text
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
    """Primary mixin that provides common behavior for SQLAlchemy models."""

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


Versioned = make_versioned_class()

metadata = MetaData(naming_convention={
  "ix": 'ix_%(column_0_label)s',
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
})

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(metadata=metadata, cls=BaseModel)
