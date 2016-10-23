import transaction
import unittest
from fanboi2.models import DBSession
from fanboi2.tests import DummyRedis, DATABASE_URI, ModelMixin
from sqlalchemy.ext.declarative import declarative_base


class TestRedisProxy(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models._redis_proxy import RedisProxy
        return RedisProxy

    def test_init(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        self.assertEqual(conn._cls, DummyRedis)
        self.assertEqual(conn._redis, None)

    def test_from_url(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        conn.from_url("redis:///")
        self.assertIsInstance(conn._redis, DummyRedis)

    def test_geattr(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        conn.from_url("redis:///")
        self.assertTrue(conn.ping())

    def test_getattr_not_initialized(self):
        conn = self._getTargetClass()(cls=DummyRedis)
        with self.assertRaises(RuntimeError):
            conn.ping()


class TestIdentity(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models._identity import Identity
        return Identity

    def _makeOne(self):
        identity = self._getTargetClass()(redis=DummyRedis())
        return identity

    def test_key(self):
        from pytz import utc
        from datetime import datetime
        identity = self._makeOne()
        self.assertTrue(
            identity._key("127.0.0.1", namespace="foobar"),
            "ident:{}:foobar:f528764d624db129b32c21fbca0cb8d6".format(
                datetime.now(utc).strftime("%Y%m%d")))

    def test_key_timezone(self):
        from pytz import timezone
        from datetime import datetime
        identity = self._makeOne()
        identity.configure_tz("Asia/Bangkok")
        self.assertTrue(
            identity._key("127.0.0.1", namespace="foobar"),
            "ident:{}:foobar:f528764d624db129b32c21fbca0cb8d6".format(
                datetime.now(timezone("Asia/Bangkok")).strftime("%Y%m%d")))

    def test_get(self):
        identity = self._makeOne()
        ident1 = identity.get("127.0.0.1")
        ident2 = identity.get("127.0.0.1", "foobar")
        ident3 = identity.get("192.168.1.1", "foobar")
        self.assertNotEqual(ident1, ident2)
        self.assertNotEqual(ident1, ident3)
        self.assertNotEqual(ident2, ident3)
        self.assertEqual(identity.get("127.0.0.1"), ident1)


class TestJsonType(unittest.TestCase):

    def _getTargetClass(self):
        from fanboi2.models import JsonType
        return JsonType

    def _makeMetaData(self):
        from sqlalchemy import MetaData, create_engine
        engine = create_engine(DATABASE_URI)
        metadata = MetaData(bind=engine)
        return metadata

    def _makeOne(self, metadata):
        from sqlalchemy import Table, Column, Integer
        table = Table(
            'foo', metadata,
            Column('baz', Integer),
            Column('bar', self._getTargetClass()),
        )
        return table

    def test_compile(self):
        self.assertEqual(str(self._getTargetClass()()), "TEXT")

    def test_field(self):
        metadata = self._makeMetaData()
        table = self._makeOne(metadata)
        metadata.drop_all()
        metadata.create_all()

        table.insert().execute(baz=1, bar={"x": 1})
        table.insert().execute(baz=2, bar=None)
        table.insert().execute(baz=3)  # bar should have default {} type.
        self.assertEqual(
            [(1, {'x': 1}), (2, None), (3, {})],
            table.select().order_by(table.c.baz).execute().fetchall()
        )

        metadata.drop_all()


class TestSerializeModel(unittest.TestCase):

    def test_serialize(self):
        from fanboi2.models import serialize_model, Board, Topic, Post
        self.assertEqual(serialize_model('board'), Board)
        self.assertEqual(serialize_model('topic'), Topic)
        self.assertEqual(serialize_model('post'), Post)
        self.assertIsNone(serialize_model('foo'))


class TestBaseModel(ModelMixin, unittest.TestCase):

    def _getTargetClass(self):
        from sqlalchemy import Column, Integer
        from fanboi2.models._base import BaseModel
        MockBase = declarative_base()

        class MockModel(BaseModel, MockBase):
            y = Column(Integer)
            x = Column(Integer)
        return MockModel

    def test_init(self):
        model_class = self._getTargetClass()
        mock = model_class(x=1, y=2)
        self.assertEqual(mock.x, 1)
        self.assertEqual(mock.y, 2)

    def test_tablename(self):
        model_class = self._getTargetClass()
        self.assertEqual(model_class.__tablename__, 'mock_model')


class TestVersioned(unittest.TestCase):

    def _makeBase(self):
        from sqlalchemy.engine import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        engine = create_engine(DATABASE_URI)
        Base = declarative_base()
        Base.metadata.bind = engine
        return Base

    def _makeSession(self, Base):
        from sqlalchemy.orm import scoped_session, sessionmaker
        from zope.sqlalchemy import ZopeTransactionExtension
        return scoped_session(
            sessionmaker(
                bind=Base.metadata.bind,
                extension=ZopeTransactionExtension()))

    def _getTargetClass(self, mappers):
        from fanboi2.models._versioned import make_versioned_class
        return make_versioned_class(lambda m: mappers.append(m))

    def _getSetupFunction(self, mappers):
        from fanboi2.models._versioned import make_versioned
        def _make_versioned(session):
            make_versioned(session, lambda: mappers)
        return _make_versioned

    def _makeTable(self, Base):
        Base.metadata.drop_all()
        Base.metadata.create_all()

    def _dropTable(self, Base):
        Base.metadata.drop_all()

    def test_versioned(self):
        from sqlalchemy.sql import func
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String, DateTime

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            body = Column(String)
            created_at = Column(DateTime(timezone=True), default=func.now())

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing(body='Hello, world')
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.body = 'Hello, galaxy'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.body, 'Hello, world')
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)
        self.assertIsNotNone(thing_v1.changed_at)
        self.assertIsNotNone(thing_v1.created_at)

        thing.body = 'Hello, universe'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 2)
        thing_v2 = Session.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_v2.body, 'Hello, galaxy')
        self.assertEqual(thing_v2.change_type, 'update')
        self.assertEqual(thing_v2.version, 2)
        self.assertIsNotNone(thing_v2.changed_at)
        self.assertIsNotNone(thing_v2.created_at)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_column(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            ref = Column(String, unique=True, info={"version_meta": True})

        self._getSetupFunction(mappers)(Session)
        thing_history_table = Thing.__history_mapper__.local_table
        self.assertIsNone(getattr(thing_history_table.c, 'ref', None))

    def test_versioned_null(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            body = Column(String, nullable=True)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing()
        Session.add(thing)
        Session.flush()
        self.assertIsNone(thing.body)
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.body = 'Hello, world'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertIsNone(thing_v1.body)
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)
        self.assertIsNotNone(thing_v1.changed_at)

        thing.body = None
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 2)
        thing_v2 = Session.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual('Hello, world', thing_v2.body)
        self.assertEqual(thing_v2.change_type, 'update')
        self.assertEqual(thing_v2.version, 2)
        self.assertIsNotNone(thing_v2.changed_at)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_bool(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, Boolean

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            boolean = Column(Boolean, default=False)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing()
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.boolean = True
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.boolean, False)
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)
        self.assertIsNotNone(thing_v1.changed_at)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_deferred(self):
        from sqlalchemy.orm import deferred
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            name = Column(String, default=False)
            data = deferred(Column(String))

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing(name='test', data='Hello, world')
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        transaction.commit()
        transaction.begin()

        thing = Session.query(Thing).first()
        thing.data = 'Hello, galaxy'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.data, 'Hello, world')
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)
        self.assertIsNotNone(thing_v1.changed_at)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_inheritance(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'

            id = Column(Integer, primary_key=True)
            name = Column(String)
            type = Column(String)

            __mapper_args__ = {
                'polymorphic_on': type,
                'polymorphic_identity': 'base',
            }

        class ThingSeparatePk(Thing):
            __tablename__ = 'thing_separate_pk'
            __mapper_args__ = {'polymorphic_identity': 'separate_pk'}

            id = column_property(Column(Integer, primary_key=True), Thing.id)
            thing_id = Column(Integer, ForeignKey('thing.id'))
            sub_data_1 = Column(String)

        class ThingSamePk(Thing):
            __tablename__ = 'thing_same_pk'
            __mapper_args__ = {'polymorphic_identity': 'same_pk'}

            id = Column(Integer, ForeignKey('thing.id'), primary_key=True)
            sub_data_2 = Column(String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        ThingSeparatePkHistory = ThingSeparatePk.__history_mapper__.class_
        ThingSamePkHistory = ThingSamePk.__history_mapper__.class_
        transaction.begin()

        thing = Thing(name='Foo')
        thing_sp = ThingSeparatePk(name='Bar', sub_data_1='Hello, world')
        thing_sm = ThingSamePk(name='Baz', sub_data_2='Hello, galaxy')
        Session.add_all([thing, thing_sp, thing_sm])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sp.version, 1)
        self.assertEqual(thing_sm.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)
        self.assertEqual(Session.query(ThingSeparatePkHistory).count(), 0)
        self.assertEqual(Session.query(ThingSamePkHistory).count(), 0)

        thing.name = 'Hoge'
        thing_sp.sub_data_1 = 'Hello, universe'
        thing_sm.sub_data_2 = 'Hello, multiuniverse'
        Session.add_all([thing, thing_sp, thing_sm])
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 2)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 3)
        self.assertEqual(Session.query(ThingSeparatePkHistory).count(), 1)
        self.assertEqual(Session.query(ThingSamePkHistory).count(), 1)

        thing_sp.sub_data_1 = 'Hello, parallel universe'
        Session.add(thing_sp)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 4)
        self.assertEqual(Session.query(ThingSeparatePkHistory).count(), 2)
        self.assertEqual(Session.query(ThingSamePkHistory).count(), 1)

        thing_sm.sub_data_2 = 'Hello, 42'
        Session.add(thing_sm)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 5)
        self.assertEqual(Session.query(ThingSeparatePkHistory).count(), 2)
        self.assertEqual(Session.query(ThingSamePkHistory).count(), 2)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_inheritance_multi(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'

            id = Column(Integer, primary_key=True)
            name = Column(String)
            type = Column(String)

            __mapper_args__ = {
                'polymorphic_on': type,
                'polymorphic_identity': 'base',
            }

        class ThingSub(Thing):
            __tablename__ = 'thing_sub'
            __mapper_args__ = {'polymorphic_identity': 'sub'}

            id = column_property(Column(Integer, primary_key=True), Thing.id)
            base_id = Column(Integer, ForeignKey('thing.id'))
            sub_data_1 = Column(String)

        class ThingSubSub(ThingSub):
            __tablename__ = 'thing_sub_sub'
            __mapper_args__ = {'polymorphic_identity': 'sub_sub'}

            id = Column(Integer, ForeignKey('thing_sub.id'), primary_key=True)
            sub_data_2 = Column(String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        ThingSubSubHistory = ThingSubSub.__history_mapper__.class_
        transaction.begin()

        thing = Thing(name='Foo')
        thing_sub = ThingSub(name='Bar', sub_data_1='Hello, world')
        thing_sub_sub = ThingSubSub(name='Baz', sub_data_2='Hello, galaxy')
        Session.add_all([thing, thing_sub, thing_sub_sub])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(thing_sub_sub.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)
        self.assertEqual(Session.query(ThingSubHistory).count(), 0)
        self.assertEqual(Session.query(ThingSubSubHistory).count(), 0)

        thing.name = 'Hoge'
        thing_sub.sub_data_1 = 'Hello, universe'
        thing_sub_sub.sub_data_2 = 'Hello, multiuniverse'
        Session.add_all([thing, thing_sub, thing_sub_sub])
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 3)
        self.assertEqual(Session.query(ThingSubHistory).count(), 2)
        self.assertEqual(Session.query(ThingSubSubHistory).count(), 1)

        thing_sub.sub_data_1 = 'Hello, parallel universe'
        Session.add(thing_sub)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 3)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 4)
        self.assertEqual(Session.query(ThingSubHistory).count(), 3)
        self.assertEqual(Session.query(ThingSubSubHistory).count(), 1)

        thing_sub_sub.sub_data_2 = 'Hello, 42'
        Session.add(thing_sub_sub)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 3)
        self.assertEqual(thing_sub_sub.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 5)
        self.assertEqual(Session.query(ThingSubHistory).count(), 4)
        self.assertEqual(Session.query(ThingSubSubHistory).count(), 2)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_inheritance_single(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'

            id = Column(Integer, primary_key=True)
            data = Column(String)
            type = Column(String)

            __mapper_args__ = {
                'polymorphic_on': type,
                'polymorphic_identity': 'base',
            }

        class ThingSub(Thing):
            __mapper_args__ = {'polymorphic_identity': 'sub'}
            sub_data = Column(String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        transaction.begin()

        thing = Thing(data='Hello, world')
        thing_sub = ThingSub(data='Hello, galaxy', sub_data='Hello, universe')
        Session.add_all([thing, thing_sub])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)
        self.assertEqual(Session.query(ThingSubHistory).count(), 0)

        thing.data = 'Hello, multiuniverse'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        self.assertEqual(Session.query(ThingSubHistory).count(), 0)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.data, 'Hello, world')
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)

        thing_sub.sub_data = 'Hello, parallel universe'
        Session.add(thing_sub)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 2)
        self.assertEqual(Session.query(ThingSubHistory).count(), 1)
        thing_sub_v1 = Session.query(ThingSubHistory).filter_by(version=1).one()
        self.assertEqual(thing_sub_v1.sub_data, 'Hello, universe')
        self.assertEqual(thing_sub_v1.change_type, 'update')
        self.assertEqual(thing_sub_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_unique(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'

            id = Column(Integer, primary_key=True)
            name = Column(String, unique=True)
            data = Column(String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing(name='Hello', data='Hello, world')
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.data = 'Hello, galaxy'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)

        thing.data = 'Hello, universe'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 2)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_relationship(self):
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Relate(Base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship('Relate', backref='things')

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing()
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        relate = Relate()
        thing.relate = relate
        Session.add_all([relate, thing])
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertIsNone(thing_v1.relate_id)
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)

        thing.relate = None
        Session.add(thing)
        Session.flush()
        self.assertIsNone(thing.relate_id)
        self.assertEqual(thing.version, 3)
        self.assertEqual(Session.query(ThingHistory).count(), 2)
        thing_v2 = Session.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_v2.relate_id, relate.id)
        self.assertEqual(thing_v2.change_type, 'update')
        self.assertEqual(thing_v2.version, 2)

        Session.delete(relate)
        Session.flush()

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_relationship_cascade_null(self):
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Relate(Base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship('Relate', backref='things')

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        relate = Relate()
        thing = Thing(relate=relate)
        Session.add_all([relate, thing])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        Session.delete(relate)
        Session.flush()
        self.assertIsNone(thing.relate_id)
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.relate_id, relate.id)
        self.assertEqual(thing_v1.change_type, 'update.cascade')
        self.assertEqual(thing_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_relationship_cascade_all(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship, backref
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Relate(Base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship(
                'Relate',
                backref=backref('things', cascade='all'))

        class Entity(self._getTargetClass(mappers), Base):
            __tablename__ = 'entity'
            id = Column(Integer, primary_key=True)
            thing_id = Column(Integer, ForeignKey('thing.id'))
            thing = relationship(
                'Thing',
                backref=backref('entities', cascade='all'))

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        EntityHistory = Entity.__history_mapper__.class_
        transaction.begin()

        relate = Relate()
        thing = Thing(relate=relate)
        entity = Entity(thing=thing)
        Session.add_all([relate, thing, entity])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(entity.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)
        self.assertEqual(Session.query(EntityHistory).count(), 0)

        Session.delete(relate)
        Session.flush()
        self.assertTrue(inspect(thing).deleted)
        self.assertTrue(inspect(entity).deleted)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        self.assertEqual(Session.query(EntityHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.relate_id, relate.id)
        self.assertEqual(thing_v1.change_type, 'delete')
        self.assertEqual(thing_v1.version, 1)
        entity_v1 = Session.query(EntityHistory).filter_by(version=1).one()
        self.assertEqual(entity_v1.thing_id, thing.id)
        self.assertEqual(entity_v1.change_type, 'delete')
        self.assertEqual(entity_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_relationship_cascade_orphan(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship, backref
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Relate(Base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship(
                'Relate',
                backref=backref('things', cascade='all,delete-orphan'))

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        relate = Relate()
        thing = Thing(relate=relate)
        Session.add_all([relate, thing])
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.relate = None
        Session.add(thing)
        Session.flush()
        self.assertTrue(inspect(thing).deleted)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.relate_id, relate.id)
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            data = Column(String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing(data='Hello, world')
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        Session.delete(thing)
        Session.flush()
        self.assertTrue(inspect(thing).deleted)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.data, 'Hello, world')
        self.assertEqual(thing_v1.change_type, 'delete')
        self.assertEqual(thing_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)

    def test_versioned_named_column(self):
        from sqlalchemy import inspect
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        Base = self._makeBase()
        Session = self._makeSession(Base)

        class Thing(self._getTargetClass(mappers), Base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            data_ = Column('data', String)

        self._getSetupFunction(mappers)(Session)
        self._makeTable(Base)
        ThingHistory = Thing.__history_mapper__.class_
        transaction.begin()

        thing = Thing(data_='Hello, world')
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 1)
        self.assertEqual(Session.query(ThingHistory).count(), 0)

        thing.data_ = 'Hello, galaxy'
        Session.add(thing)
        Session.flush()
        self.assertEqual(thing.version, 2)
        self.assertEqual(Session.query(ThingHistory).count(), 1)
        thing_v1 = Session.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_v1.data_, 'Hello, world')
        self.assertEqual(thing_v1.change_type, 'update')
        self.assertEqual(thing_v1.version, 1)

        transaction.abort()
        self._dropTable(Base)


class TestBoardModel(ModelMixin, unittest.TestCase):

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        self.assertEqual([], list(board.topics))

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        board1 = self._makeBoard(title="Foobar", slug="foo")
        board2 = self._makeBoard(title="Lorem", slug="lorem")
        topic1 = self._makeTopic(board=board1, title="Heavenly Moon")
        topic2 = self._makeTopic(board=board1, title="Beastie Starter")
        topic3 = self._makeTopic(board=board2, title="Evans")
        post1 = self._makePost(topic=topic1, body='Foobar')
        post2 = self._makePost(topic=topic1, body='Bazz')
        post3 = self._makePost(topic=topic2, body='Hoge')
        post4 = self._makePost(topic=topic3, body='Fuzz')
        self.assertEqual({topic2, topic1}, set(board1.topics))
        self.assertEqual({topic3}, set(board2.topics))
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        self.assertEqual({post4}, set(topic3.posts))
        DBSession.delete(board1)
        DBSession.flush()
        self.assertTrue(inspect(board1).deleted)
        self.assertFalse(inspect(board2).deleted)
        self.assertTrue(inspect(topic1).deleted)
        self.assertTrue(inspect(topic2).deleted)
        self.assertFalse(inspect(topic3).deleted)
        self.assertTrue(inspect(post1).deleted)
        self.assertTrue(inspect(post2).deleted)
        self.assertTrue(inspect(post3).deleted)
        self.assertFalse(inspect(post4).deleted)

    def test_versioned(self):
        from fanboi2.models import Board
        BoardHistory = Board.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        self.assertEqual(board.version, 1)
        self.assertEqual(DBSession.query(BoardHistory).count(), 0)
        board.title = 'Foobar and Baz'
        DBSession.add(board)
        DBSession.flush()
        self.assertEqual(board.version, 2)
        self.assertEqual(DBSession.query(BoardHistory).count(), 1)
        board_v1 = DBSession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_v1.id, board.id)
        self.assertEqual(board_v1.title, 'Foobar')
        self.assertEqual(board_v1.change_type, 'update')
        self.assertEqual(board_v1.version, 1)
        self.assertIsNotNone(board_v1.changed_at)
        self.assertIsNotNone(board_v1.created_at)
        self.assertIsNone(board_v1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from fanboi2.models import Board
        BoardHistory = Board.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        DBSession.delete(board)
        DBSession.flush()
        self.assertTrue(inspect(board).deleted)
        self.assertEqual(DBSession.query(BoardHistory).count(), 1)
        board_v1 = DBSession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_v1.id, board.id)
        self.assertEqual(board_v1.title, 'Foobar')
        self.assertEqual(board_v1.change_type, 'delete')
        self.assertEqual(board_v1.version, 1)

    def test_versioned_deleted_cascade(self):
        from sqlalchemy import inspect
        from fanboi2.models import Board, Topic, Post
        BoardHistory = Board.__history_mapper__.class_
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Heavenly Moon')
        post = self._makePost(topic=topic, body='Foobar')
        self.assertEqual(DBSession.query(BoardHistory).count(), 0)
        self.assertEqual(DBSession.query(TopicHistory).count(), 0)
        self.assertEqual(DBSession.query(PostHistory).count(), 0)
        DBSession.delete(board)
        DBSession.flush()
        self.assertEqual(DBSession.query(BoardHistory).count(), 1)
        self.assertEqual(DBSession.query(TopicHistory).count(), 1)
        self.assertEqual(DBSession.query(PostHistory).count(), 1)
        board_v1 = DBSession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_v1.id, board.id)
        self.assertEqual(board_v1.change_type, 'delete')
        self.assertEqual(board_v1.version, 1)
        topic_v1 = DBSession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_v1.id, topic.id)
        self.assertEqual(topic_v1.board_id, board.id)
        self.assertEqual(topic_v1.change_type, 'delete')
        self.assertEqual(topic_v1.version, 1)
        post_v1 = DBSession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_v1.id, post.id)
        self.assertEqual(post_v1.topic_id, topic.id)
        self.assertEqual(post_v1.change_type, 'delete')
        self.assertEqual(post_v1.version, 1)

    def test_settings(self):
        from fanboi2.models.board import DEFAULT_BOARD_CONFIG
        board = self._makeBoard(title="Foobar", slug="Foo")
        self.assertEqual(board.settings, DEFAULT_BOARD_CONFIG)
        board.settings = {'name': 'Hamster'}
        new_settings = DEFAULT_BOARD_CONFIG.copy()
        new_settings.update({'name': 'Hamster'})
        DBSession.add(board)
        DBSession.flush()
        self.assertEqual(board.settings, new_settings)

    def test_topics(self):
        from fanboi2.models import Topic
        board1 = self._makeBoard(title="Foobar", slug="foo")
        board2 = self._makeBoard(title="Lorem", slug="lorem")
        topic1 = self._makeTopic(board=board1, title="Heavenly Moon")
        topic2 = self._makeTopic(board=board1, title="Beastie Starter")
        topic3 = self._makeTopic(board=board1, title="Evans")
        DBSession.flush()
        self.assertEqual({topic3, topic2, topic1}, set(board1.topics))
        self.assertEqual([], list(board2.topics))

    def test_topics_sort(self):
        from datetime import datetime, timedelta
        from fanboi2.models import Topic, Post
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="First")
        topic2 = self._makeTopic(board=board, title="Second")
        topic3 = self._makeTopic(board=board, title="Third")
        topic4 = self._makeTopic(board=board, title="Fourth")
        topic5 = self._makeTopic(
            board=board,
            title="Fifth",
            created_at=datetime.now() + timedelta(seconds=10))
        self._makePost(topic=topic1, ip_address="1.1.1.1", body="!!1")
        self._makePost(topic=topic4, ip_address="1.1.1.1", body="Baz")
        mappings = ((topic3, 3, True), (topic2, 5, True), (topic4, 8, False))
        for obj, offset, bump in mappings:
            self._makePost(
                topic=obj,
                ip_address="1.1.1.1",
                body="Foo",
                created_at=datetime.now() + timedelta(seconds=offset),
                bumped=bump)
        self._makePost(
            topic=topic5,
            ip_address="1.1.1.1",
            body="Hax",
            bumped=False)
        DBSession.refresh(board)
        self.assertEqual([topic5, topic2, topic3, topic1, topic4],
                         list(board.topics))


class TestTopicModel(ModelMixin, unittest.TestCase):

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from fanboi2.models import Post
        board = self._makeBoard(title='Foobar', slug='foo')
        topic1 = self._makeTopic(board=board, title='Shamshir Dance')
        topic2 = self._makeTopic(board=board, title='Nyoah Sword Dance')
        post1 = self._makePost(topic=topic1, body='Lorem ipsum')
        post2 = self._makePost(topic=topic1, body='Dolor sit amet')
        post3 = self._makePost(topic=topic2, body='Quas magnam et')
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        DBSession.delete(topic1)
        DBSession.flush()
        self.assertTrue(inspect(topic1).deleted)
        self.assertFalse(inspect(topic2).deleted)
        self.assertTrue(inspect(post1).deleted)
        self.assertTrue(inspect(post2).deleted)
        self.assertFalse(inspect(post3).deleted)

    def test_versioned(self):
        from fanboi2.models import Topic
        TopicHistory = Topic.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Foobar')
        self.assertEqual(topic.version, 1)
        self.assertEqual(DBSession.query(TopicHistory).count(), 0)
        topic.title = 'Foobar Baz'
        DBSession.add(topic)
        DBSession.flush()
        self.assertEqual(topic.version, 2)
        self.assertEqual(DBSession.query(TopicHistory).count(), 1)
        topic_v1 = DBSession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_v1.id, topic.id)
        self.assertEqual(topic_v1.board_id, topic.board_id)
        self.assertEqual(topic_v1.title, 'Foobar')
        self.assertEqual(topic_v1.change_type, 'update')
        self.assertEqual(topic_v1.version, 1)
        self.assertIsNotNone(topic_v1.changed_at)
        self.assertIsNotNone(topic_v1.created_at)
        self.assertIsNone(topic_v1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from fanboi2.models import Topic
        TopicHistory = Topic.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Foobar')
        DBSession.delete(topic)
        DBSession.flush()
        self.assertTrue(inspect(topic).deleted)
        self.assertEqual(DBSession.query(TopicHistory).count(), 1)
        topic_v1 = DBSession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_v1.id, topic.id)
        self.assertEqual(topic_v1.board_id, topic.board_id)
        self.assertEqual(topic_v1.title, 'Foobar')
        self.assertEqual(topic_v1.change_type, 'delete')
        self.assertEqual(topic_v1.version, 1)

    def test_versioned_deleted_cascade(self):
        from sqlalchemy import inspect
        from fanboi2.models import Topic, Post
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Cosmic Agenda')
        post = self._makePost(topic=topic, body='Foobar')
        self.assertEqual(DBSession.query(TopicHistory).count(), 0)
        self.assertEqual(DBSession.query(PostHistory).count(), 0)
        DBSession.delete(topic)
        DBSession.flush()
        self.assertEqual(DBSession.query(TopicHistory).count(), 1)
        self.assertEqual(DBSession.query(PostHistory).count(), 1)
        topic_v1 = DBSession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_v1.id, topic.id)
        self.assertEqual(topic_v1.board_id, board.id)
        self.assertEqual(topic_v1.change_type, 'delete')
        self.assertEqual(topic_v1.version, 1)
        post_v1 = DBSession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_v1.id, post.id)
        self.assertEqual(post_v1.topic_id, topic.id)
        self.assertEqual(post_v1.change_type, 'delete')
        self.assertEqual(post_v1.version, 1)

    def test_posts(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board, title="Lorem ipsum dolor")
        topic2 = self._makeTopic(board=board, title="Some lonely topic")
        post1 = self._makePost(topic=topic1, body='Lorem')
        post2 = self._makePost(topic=topic1, body='Ipsum')
        post3 = self._makePost(topic=topic1, body='Dolor')
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_auto_archive(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 5,
        })
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        for i in range(4):
            self._makePost(topic=topic, body="Post %s" % i)
        self.assertEqual(topic.status, "open")
        self._makePost(topic=topic, body="Post 5")
        self.assertEqual(topic.status, "archived")

    def test_auto_archive_locked(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'max_posts': 3,
        })
        topic = self._makeTopic(board=board,
                                title="Lorem ipsum dolor",
                                status='locked')
        for i in range(3):
            post = self._makePost(topic=topic, body="Post %s" % i)
        self.assertEqual(topic.status, "locked")

    def test_post_count(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in range(3):
            self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.post_count, 3)

    def test_post_count_missing(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertEqual(topic.post_count, 0)
        for x in range(2):
            self._makePost(topic=topic, body="Hello, world!")
        post = self._makePost(topic=topic, body="Hello, world!")
        self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.post_count, 4)
        DBSession.delete(post)
        DBSession.flush()
        DBSession.expire(topic, ['post_count'])
        self.assertEqual(topic.post_count, 4)

    def test_posted_at(self):
        from datetime import datetime, timezone
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertIsNone(topic.posted_at)
        for x in range(2):
            self._makePost(
                topic=topic,
                body="Hello, world!",
                created_at=datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc))
        post = self._makePost(topic=topic, body="Hello, world!")
        self.assertEqual(topic.created_at, post.created_at)

    def test_bumped_at(self):
        from datetime import datetime, timezone
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor")
        self.assertIsNone(topic.bumped_at)
        post1 = self._makePost(
            topic=topic,
            body="Hello, world",
            created_at=datetime(2013, 1, 2, 0, 4, 1, 0, timezone.utc))
        post2 = self._makePost(topic=topic, body="Spam!", bumped=False)
        self.assertEqual(topic.bumped_at, post1.created_at)
        self.assertNotEqual(topic.bumped_at, post2.created_at)

    def test_scoped_posts(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Post 1")
        post2 = self._makePost(topic=topic, body="Post 2")
        post3 = self._makePost(topic=topic, body="Post 3")
        self.assertListEqual(topic.scoped_posts(None), [post1, post2, post3])
        self.assertListEqual(topic.scoped_posts("bogus"), [])

    def test_single_post(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another post!!1")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Post 1")
        post2 = self._makePost(topic=topic2, body="Post 1")
        post3 = self._makePost(topic=topic1, body="Post 2")
        post4 = self._makePost(topic=topic2, body="Post 2")
        results = topic1.single_post(2)
        self.assertListEqual(results, [post3])
        self.assertListEqual(results, topic1.scoped_posts("2"))
        self.assertListEqual(topic1.single_post(1000), [])
        self.assertListEqual(topic3.single_post(1), [])
        self.assertListEqual(topic3.single_post(), [])

    def test_ranged_posts(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(2, 5)
        self.assertListEqual(results, [post2, post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("2-5"))
        self.assertListEqual(topic1.ranged_posts(1000, 1005), [])
        self.assertListEqual(topic3.ranged_posts(1, 5), [])
        self.assertListEqual(topic1.ranged_posts(), topic1.posts.all())

    def test_ranged_posts_without_end(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(3)
        self.assertListEqual(results, [post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("3-"))
        self.assertListEqual(topic1.ranged_posts(1000), [])
        self.assertListEqual(topic3.ranged_posts(3), [])

    def test_range_query_without_start(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        post3 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 4")
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 1")
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 2")
        post7 = self._makePost(topic=topic1, body="Topic 1, Post 5")
        results = topic1.ranged_posts(None, 3)
        self.assertListEqual(results, [post1, post2, post3])
        self.assertListEqual(results, topic1.scoped_posts("-3"))
        self.assertListEqual(topic1.ranged_posts(None, 0), [])
        self.assertListEqual(topic3.ranged_posts(None, 3), [])

    def test_recent_query(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic1 = self._makeTopic(board=board, title="Hello, world!")
        topic2 = self._makeTopic(board=board, title="Another test")
        topic3 = self._makeTopic(board=board, title="Empty topic")
        post1 = self._makePost(topic=topic1, body="Topic 1, Post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, Post 2")
        [self._makePost(topic=topic2, body="Foobar") for i in range(5)]
        post3 = self._makePost(topic=topic2, body="Topic 2, Post 6")
        post4 = self._makePost(topic=topic1, body="Topic 1, Post 3")
        [self._makePost(topic=topic2, body="Foobar") for i in range(24)]
        post5 = self._makePost(topic=topic2, body="Topic 2, Post 31")
        [self._makePost(topic=topic2, body="Foobar") for i in range(3)]
        post6 = self._makePost(topic=topic2, body="Topic 2, Post 35")

        default_results = topic2.recent_posts()
        self.assertEqual(default_results[0], post3)
        self.assertEqual(default_results[-1], post6)
        self.assertListEqual(default_results, topic2.scoped_posts("recent"))

        numbered_results = topic2.recent_posts(5)
        self.assertEqual(numbered_results[0], post5)
        self.assertEqual(numbered_results[-1], post6)
        self.assertListEqual(numbered_results, topic2.scoped_posts("l5"))

        self.assertListEqual(topic2.recent_posts(0), [])
        self.assertListEqual(topic3.recent_posts(), [])

    def test_recent_query_missing(self):
        board = self._makeBoard(title="Foobar", slug="foobar")
        topic = self._makeTopic(board=board, title="Hello, world!")
        post1 = self._makePost(topic=topic, body="Post 1")
        post2 = self._makePost(topic=topic, body="Post 2")
        post3 = self._makePost(topic=topic, body="Post 3")
        post4 = self._makePost(topic=topic, body="Post 4")
        post5 = self._makePost(topic=topic, body="Post 5")
        post6 = self._makePost(topic=topic, body="Post 6")
        self.assertListEqual(
            [post2, post3, post4, post5, post6],
            topic.scoped_posts("l5"))

        DBSession.delete(post3)
        DBSession.flush()
        self.assertListEqual(
            [post1, post2, post4, post5, post6],
            topic.scoped_posts("l5"))


class TestPostModel(ModelMixin, unittest.TestCase):

    def test_relations(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post = self._makePost(topic=topic, body="Hello, world")
        self.assertEqual(post.topic, topic)
        self.assertEqual([post], list(topic.posts))

    def test_versioned(self):
        from fanboi2.models import Post
        PostHistory = Post.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Lorem ipsum dolor')
        post = self._makePost(topic=topic, body='Foobar baz')
        self.assertEqual(post.version, 1)
        self.assertEqual(DBSession.query(PostHistory).count(), 0)
        post.body = 'Foobar baz updated'
        DBSession.add(post)
        DBSession.flush()
        self.assertEqual(post.version, 2)
        self.assertEqual(DBSession.query(PostHistory).count(), 1)
        post_v1 = DBSession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_v1.id, post.id)
        self.assertEqual(post_v1.topic_id, topic.id)
        self.assertEqual(post_v1.body, 'Foobar baz')
        self.assertEqual(post_v1.version, 1)
        self.assertIsNotNone(post_v1.changed_at)
        self.assertIsNotNone(post_v1.created_at)
        self.assertIsNone(post_v1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from fanboi2.models import Post
        PostHistory = Post.__history_mapper__.class_
        board = self._makeBoard(title='Foobar', slug='foo')
        topic = self._makeTopic(board=board, title='Lorem ipsum dolor')
        post = self._makePost(topic=topic, body='Foobar baz')
        DBSession.delete(post)
        DBSession.flush()
        self.assertTrue(inspect(post).deleted)
        self.assertEqual(DBSession.query(PostHistory).count(), 1)
        post_v1 = DBSession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_v1.id, post.id)
        self.assertEqual(post_v1.topic_id, topic.id)
        self.assertEqual(post_v1.body, 'Foobar baz')
        self.assertEqual(post_v1.change_type, 'delete')
        self.assertEqual(post_v1.version, 1)

    def test_number(self):
        board = self._makeBoard(title="Foobar", slug="foo")
        topic1 = self._makeTopic(board=board, title="Numbering one")
        topic2 = self._makeTopic(board=board, title="Numbering two")
        post1 = self._makePost(topic=topic1, body="Topic 1, post 1")
        post2 = self._makePost(topic=topic1, body="Topic 1, post 2")
        post3 = self._makePost(topic=topic2, body="Topic 2, post 1")
        post4 = self._makePost(topic=topic1, body="Topic 1, post 3")
        post5 = self._makePost(topic=topic2, body="Topic 2, post 2")
        # Force update to ensure its number remain the same.
        post4.body = "Topic1, post 3, updated!"
        DBSession.add(post4)
        DBSession.flush()
        self.assertEqual(post1.number, 1)
        self.assertEqual(post2.number, 2)
        self.assertEqual(post3.number, 1)
        self.assertEqual(post4.number, 3)
        self.assertEqual(post5.number, 2)

    def test_name(self):
        board = self._makeBoard(title="Foobar", slug="foo", settings={
            'name': 'Nobody Nowhere',
        })
        topic = self._makeTopic(board=board, title="No name!")
        post1 = self._makePost(topic=topic, body="I'm nameless")
        post2 = self._makePost(topic=topic, body="I have a name", name="John")
        self.assertEqual(post1.name, "Nobody Nowhere")
        self.assertEqual(post2.name, "John")

    def test_ident(self):
        board = self._makeBoard(title="Testbed", slug="test")
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hi", ip_address="127.0.0.1")
        post2 = self._makePost(topic=topic, body="Yo", ip_address="10.0.1.18")
        post3 = self._makePost(topic=topic, body="Hey", ip_address="10.0.1.1")
        post4 = self._makePost(topic=topic, body="!!", ip_address="127.0.0.1")
        self.assertIsInstance(post1.ident, str)
        self.assertIsInstance(post4.ident, str)
        self.assertNotEqual(post1.ident, post2.ident)
        self.assertNotEqual(post1.ident, post3.ident)
        self.assertNotEqual(post2.ident, post3.ident)
        self.assertEqual(post1.ident, post4.ident)

    def test_ident_disabled(self):
        board = self._makeBoard(title="Testbed", slug="test", settings={
            'use_ident': False,
        })
        topic = self._makeTopic(board=board, title="Lorem ipsum dolor sit")
        post1 = self._makePost(topic=topic, body="Hi", ip_address="127.0.0.1")
        post2 = self._makePost(topic=topic, body="Yo", ip_address="10.0.2.8")
        self.assertIsNone(post1.ident)
        self.assertIsNone(post2.ident)

    def test_ident_namespaced(self):
        board1 = self._makeBoard(title="Test 1", slug="test1")
        board2 = self._makeBoard(title="Test 2", slug="test2")
        topic1 = self._makeTopic(board=board1, title="First topic")
        topic2 = self._makeTopic(board=board2, title="Second topic")
        p1 = self._makePost(topic=topic1, body="Test", ip_address="10.0.1.1")
        p2 = self._makePost(topic=topic2, body="Test", ip_address="10.0.1.1")
        self.assertNotEqual(p1.ident, p2.ident)
