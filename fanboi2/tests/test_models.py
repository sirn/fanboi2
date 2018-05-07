import unittest

from sqlalchemy.ext.declarative import declarative_base

from . import ModelTransactionEngineMixin, ModelSessionMixin


class TestDeserializeModel(unittest.TestCase):

    def test_serialize(self):
        from ..models import deserialize_model
        from ..models import Board, Group, Page, Post, Rule, RuleBan
        from ..models import Setting, Topic, TopicMeta, User, UserSession
        self.assertEqual(deserialize_model('board'), Board)
        self.assertEqual(deserialize_model('group'), Group)
        self.assertEqual(deserialize_model('page'), Page)
        self.assertEqual(deserialize_model('post'), Post)
        self.assertEqual(deserialize_model('rule'), Rule)
        self.assertEqual(deserialize_model('rule_ban'), RuleBan)
        self.assertEqual(deserialize_model('setting'), Setting)
        self.assertEqual(deserialize_model('topic'), Topic)
        self.assertEqual(deserialize_model('topic_meta'), TopicMeta)
        self.assertEqual(deserialize_model('user'), User)
        self.assertEqual(deserialize_model('user_session'), UserSession)
        self.assertIsNone(deserialize_model('foo'))


class TestBaseModel(unittest.TestCase):

    def _get_target_class(self):
        from sqlalchemy import Column, Integer
        from ..models._base import BaseModel
        MockBase = declarative_base()

        class MockModel(BaseModel, MockBase):
            __tablename__ = 'mock'
            id = Column(Integer, primary_key=True)
            y = Column(Integer)
            x = Column(Integer)
        return MockModel

    def test_init(self):
        model_class = self._get_target_class()
        mock = model_class(x=1, y=2)
        self.assertEqual(mock.x, 1)
        self.assertEqual(mock.y, 2)


class TestVersioned(ModelTransactionEngineMixin, unittest.TestCase):

    def setUp(self):
        super(TestVersioned, self).setUp()
        from sqlalchemy import event
        from sqlalchemy.orm import sessionmaker
        from ..models._versioned import make_history_event
        local_dbmaker = sessionmaker()
        self.dbsession = local_dbmaker(bind=self.connection)
        make_history_event(self.dbsession)

        @event.listens_for(self.dbsession, "after_transaction_end")
        def restart_savepoint(dbsession, transaction):  # pragma: no cover
            if transaction.nested and not transaction._parent.nested:
                dbsession.expire_all()
                dbsession.begin_nested()

    def tearDown(self):
        super(TestVersioned, self).tearDown()
        self.dbsession.close()

    def _make_base(self):
        base = declarative_base()
        base.metadata.bind = self.connection
        return base

    def _get_target_class(self, mappers):
        from ..models._versioned import make_versioned_class
        return make_versioned_class(lambda m: mappers.append(m))

    def _get_setup_function(self, mappers):
        from ..models._versioned import setup_versioned

        def _setup_versioned(session):
            setup_versioned(lambda: mappers)
        return _setup_versioned

    def test_versioned(self):
        from sqlalchemy.sql import func
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String, DateTime
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            body = Column(String)
            created_at = Column(DateTime(timezone=True), default=func.now())

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(body='Hello, world')
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.body = 'Hello, galaxy'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.body, 'Hello, world')
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)
        self.assertIsNotNone(thing_1.created_at)
        thing.body = 'Hello, universe'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_2.body, 'Hello, galaxy')
        self.assertEqual(thing_2.change_type, 'update')
        self.assertEqual(thing_2.version, 2)
        self.assertIsNotNone(thing_2.changed_at)
        self.assertIsNotNone(thing_2.created_at)

    def test_versioned_column(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            ref = Column(String, unique=True, info={"version_meta": True})

        self._get_setup_function(mappers)(self.dbsession)
        thing_history_table = Thing.__history_mapper__.local_table
        self.assertIsNone(getattr(thing_history_table.c, 'ref', None))

    def test_versioned_null(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            body = Column(String, nullable=True)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing()
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertIsNone(thing.body)
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.body = 'Hello, world'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertIsNone(thing_1.body)
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)
        thing.body = None
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual('Hello, world', thing_2.body)
        self.assertEqual(thing_2.change_type, 'update')
        self.assertEqual(thing_2.version, 2)
        self.assertIsNotNone(thing_2.changed_at)

    def test_versioned_bool(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, Boolean
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            boolean = Column(Boolean, default=False)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing()
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.boolean = True
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.boolean, False)
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)

    def test_versioned_deferred(self):
        from sqlalchemy.orm import deferred
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            name = Column(String, default=False)
            data = deferred(Column(String))

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(name='test', data='Hello, world')
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.dbsession.commit()
        thing = self.dbsession.query(Thing).first()
        thing.data = 'Hello, galaxy'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, 'Hello, world')
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)

    def test_versioned_inheritance(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
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

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSeparatePkHistory = ThingSeparatePk.__history_mapper__.class_
        ThingSamePkHistory = ThingSamePk.__history_mapper__.class_
        thing = Thing(name='Foo')
        thing_sp = ThingSeparatePk(name='Bar', sub_data_1='Hello, world')
        thing_sm = ThingSamePk(name='Baz', sub_data_2='Hello, galaxy')
        self.dbsession.add_all([thing, thing_sp, thing_sm])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sp.version, 1)
        self.assertEqual(thing_sm.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(
            self.dbsession.query(ThingSeparatePkHistory).count(),
            0)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 0)
        thing.name = 'Hoge'
        thing_sp.sub_data_1 = 'Hello, universe'
        thing_sm.sub_data_2 = 'Hello, multiuniverse'
        self.dbsession.add_all([thing, thing_sp, thing_sm])
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 2)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 3)
        self.assertEqual(
            self.dbsession.query(ThingSeparatePkHistory).count(),
            1)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 1)
        thing_sp.sub_data_1 = 'Hello, parallel universe'
        self.dbsession.add(thing_sp)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 4)
        self.assertEqual(
            self.dbsession.query(ThingSeparatePkHistory).count(),
            2)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 1)
        thing_sm.sub_data_2 = 'Hello, 42'
        self.dbsession.add(thing_sm)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 5)
        self.assertEqual(
            self.dbsession.query(ThingSeparatePkHistory).count(),
            2)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 2)

    def test_versioned_inheritance_multi(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
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

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        ThingSubSubHistory = ThingSubSub.__history_mapper__.class_
        thing = Thing(name='Foo')
        thing_sub = ThingSub(name='Bar', sub_data_1='Hello, world')
        thing_sub_sub = ThingSubSub(name='Baz', sub_data_2='Hello, galaxy')
        self.dbsession.add_all([thing, thing_sub, thing_sub_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(thing_sub_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 0)
        thing.name = 'Hoge'
        thing_sub.sub_data_1 = 'Hello, universe'
        thing_sub_sub.sub_data_2 = 'Hello, multiuniverse'
        self.dbsession.add_all([thing, thing_sub, thing_sub_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 3)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 1)
        thing_sub.sub_data_1 = 'Hello, parallel universe'
        self.dbsession.add(thing_sub)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 3)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 4)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 3)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 1)
        thing_sub_sub.sub_data_2 = 'Hello, 42'
        self.dbsession.add(thing_sub_sub)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 3)
        self.assertEqual(thing_sub_sub.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 5)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 4)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 2)

    def test_versioned_inheritance_single(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
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

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        thing = Thing(data='Hello, world')
        thing_sub = ThingSub(data='Hello, galaxy', sub_data='Hello, universe')
        self.dbsession.add_all([thing, thing_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        thing.data = 'Hello, multiuniverse'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, 'Hello, world')
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        thing_sub.sub_data = 'Hello, parallel universe'
        self.dbsession.add(thing_sub)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 1)
        thing_sub_1 = self.dbsession.query(ThingSubHistory).\
            filter_by(version=1).\
            one()
        self.assertEqual(thing_sub_1.sub_data, 'Hello, universe')
        self.assertEqual(thing_sub_1.change_type, 'update')
        self.assertEqual(thing_sub_1.version, 1)

    def test_versioned_unique(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'

            id = Column(Integer, primary_key=True)
            name = Column(String, unique=True)
            data = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(name='Hello', data='Hello, world')
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.data = 'Hello, galaxy'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing.data = 'Hello, universe'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)

    def test_versioned_relationship(self):
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer
        mappers = []
        base = self._make_base()

        class Relate(base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship('Relate', backref='things')

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing()
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        relate = Relate()
        thing.relate = relate
        self.dbsession.add_all([relate, thing])
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertIsNone(thing_1.relate_id)
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)
        thing.relate = None
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertIsNone(thing.relate_id)
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_2.relate_id, relate.id)
        self.assertEqual(thing_2.change_type, 'update')
        self.assertEqual(thing_2.version, 2)

    def test_versioned_relationship_cascade_null(self):
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer
        mappers = []
        base = self._make_base()

        class Relate(base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship('Relate', backref='things')

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        relate = Relate()
        thing = Thing(relate=relate)
        self.dbsession.add_all([relate, thing])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.dbsession.delete(relate)
        self.dbsession.commit()
        self.assertIsNone(thing.relate_id)
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.relate_id, relate.id)
        self.assertEqual(thing_1.change_type, 'update.cascade')
        self.assertEqual(thing_1.version, 1)

    def test_versioned_relationship_cascade_null_parent(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer
        mappers = []
        base = self._make_base()
        versioned = self._get_target_class(mappers)

        class Relate(versioned, base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(versioned, base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship('Relate', backref='things')

        class Child(versioned, base):
            __tablename__ = 'child'
            id = Column(Integer, primary_key=True)
            thing_id = Column(Integer, ForeignKey('thing.id'))
            thing = relationship('Thing', backref='children')

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        RelateHistory = Relate.__history_mapper__.class_
        ThingHistory = Thing.__history_mapper__.class_
        ChildHistory = Child.__history_mapper__.class_
        relate = Relate()
        thing = Thing(relate=relate)
        child = Child(thing=thing)
        self.dbsession.add_all([relate, thing, child])
        self.dbsession.commit()
        self.assertEqual(relate.version, 1)
        self.assertEqual(thing.version, 1)
        self.assertEqual(child.version, 1)
        self.assertEqual(self.dbsession.query(RelateHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ChildHistory).count(), 0)
        self.dbsession.delete(thing)
        self.dbsession.commit()
        self.assertTrue(inspect(thing).was_deleted)
        self.assertEqual(relate.version, 1)
        self.assertEqual(child.version, 2)
        self.assertEqual(self.dbsession.query(RelateHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        self.assertEqual(self.dbsession.query(ChildHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.relate_id, relate.id)
        self.assertEqual(thing_1.change_type, 'delete')
        self.assertEqual(thing_1.version, 1)
        child_1 = self.dbsession.query(ChildHistory).filter_by(version=1).one()
        self.assertEqual(child_1.thing_id, thing.id)
        self.assertEqual(child_1.change_type, 'update.cascade')
        self.assertEqual(child_1.version, 1)

    def test_versioned_relationship_cascade_all(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship, backref
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer
        mappers = []
        base = self._make_base()
        versioned = self._get_target_class(mappers)

        class Relate(base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(versioned, base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship(
                'Relate',
                backref=backref('things', cascade='all'))

        class Entity(versioned, base):
            __tablename__ = 'entity'
            id = Column(Integer, primary_key=True)
            thing_id = Column(Integer, ForeignKey('thing.id'))
            thing = relationship(
                'Thing',
                backref=backref('entities', cascade='all'))

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        EntityHistory = Entity.__history_mapper__.class_
        relate = Relate()
        thing = Thing(relate=relate)
        entity = Entity(thing=thing)
        self.dbsession.add_all([relate, thing, entity])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(entity.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(EntityHistory).count(), 0)
        self.dbsession.delete(relate)
        self.dbsession.commit()
        self.assertTrue(inspect(thing).was_deleted)
        self.assertTrue(inspect(entity).was_deleted)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        self.assertEqual(self.dbsession.query(EntityHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.relate_id, relate.id)
        self.assertEqual(thing_1.change_type, 'delete')
        self.assertEqual(thing_1.version, 1)
        entity_1 = self.dbsession.query(EntityHistory).\
            filter_by(version=1).\
            one()
        self.assertEqual(entity_1.thing_id, thing.id)
        self.assertEqual(entity_1.change_type, 'delete')
        self.assertEqual(entity_1.version, 1)

    def test_versioned_relationship_cascade_orphan(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship, backref
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer
        mappers = []
        base = self._make_base()

        class Relate(base):
            __tablename__ = 'relate'
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey('relate.id'))
            relate = relationship(
                'Relate',
                backref=backref('things', cascade='all,delete-orphan'))

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        relate = Relate()
        thing = Thing(relate=relate)
        self.dbsession.add_all([relate, thing])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.relate = None
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertTrue(inspect(thing).was_deleted)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.relate_id, relate.id)
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            data = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(data='Hello, world')
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.dbsession.delete(thing)
        self.dbsession.commit()
        self.assertTrue(inspect(thing).was_deleted)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, 'Hello, world')
        self.assertEqual(thing_1.change_type, 'delete')
        self.assertEqual(thing_1.version, 1)

    def test_versioned_named_column(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String
        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            data_ = Column('data', String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(data_='Hello, world')
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.data_ = 'Hello, galaxy'
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data_, 'Hello, world')
        self.assertEqual(thing_1.change_type, 'update')
        self.assertEqual(thing_1.version, 1)


class TestBoardModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from ..models import Board
        board = self._make(Board(title="Foobar", slug="foo"))
        self.dbsession.commit()
        self.assertEqual([], list(board.topics))

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post
        board1 = self._make(Board(title="Foobar", slug="foo"))
        board2 = self._make(Board(title="Lorem", slug="lorem"))
        topic1 = self._make(Topic(board=board1, title="Heavenly Moon"))
        topic2 = self._make(Topic(board=board1, title="Beastie Starter"))
        topic3 = self._make(Topic(board=board2, title="Evans"))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=2))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=1))
        topic_meta3 = self._make(TopicMeta(topic=topic3, post_count=1))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Bazz',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Hoge',
            ip_address='127.0.0.1'))
        post4 = self._make(Post(
            topic=topic3,
            number=1,
            name='Nameless Fanboi',
            body='Fuzz',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual({topic2, topic1}, set(board1.topics))
        self.assertEqual({topic3}, set(board2.topics))
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        self.assertEqual({post4}, set(topic3.posts))
        self.dbsession.delete(board1)
        self.dbsession.commit()
        self.assertTrue(inspect(board1).was_deleted)
        self.assertFalse(inspect(board2).was_deleted)
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertTrue(inspect(topic2).was_deleted)
        self.assertFalse(inspect(topic3).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertTrue(inspect(topic_meta2).was_deleted)
        self.assertFalse(inspect(topic_meta3).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertTrue(inspect(post3).was_deleted)
        self.assertFalse(inspect(post4).was_deleted)

    def test_versioned(self):
        from ..models import Board
        BoardHistory = Board.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        self.assertEqual(board.version, 1)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        board.title = 'Foobar and Baz'
        self.dbsession.add(board)
        self.dbsession.commit()
        self.assertEqual(board.version, 2)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.title, 'Foobar')
        self.assertEqual(board_1.change_type, 'update')
        self.assertEqual(board_1.version, 1)
        self.assertIsNotNone(board_1.changed_at)
        self.assertIsNotNone(board_1.created_at)
        self.assertIsNone(board_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board
        BoardHistory = Board.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        self.dbsession.commit()
        self.dbsession.delete(board)
        self.dbsession.commit()
        self.assertTrue(inspect(board).was_deleted)
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.title, 'Foobar')
        self.assertEqual(board_1.change_type, 'delete')
        self.assertEqual(board_1.version, 1)

    def test_versioned_deleted_cascade(self):
        from ..models import Board, Topic, Post
        BoardHistory = Board.__history_mapper__.class_
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Heavenly Moon'))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        self.dbsession.delete(board)
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 1)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        board_1 = self.dbsession.query(BoardHistory).filter_by(version=1).one()
        self.assertEqual(board_1.id, board.id)
        self.assertEqual(board_1.change_type, 'delete')
        self.assertEqual(board_1.version, 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, board.id)
        self.assertEqual(topic_1.change_type, 'delete')
        self.assertEqual(topic_1.version, 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.change_type, 'delete')
        self.assertEqual(post_1.version, 1)

    def test_settings(self):
        from ..models import Board
        from ..models.board import DEFAULT_BOARD_CONFIG
        board = self._make(Board(title="Foobar", slug="Foo"))
        self.assertEqual(board.settings, DEFAULT_BOARD_CONFIG)
        board.settings = {'name': 'Hamster'}
        new_settings = DEFAULT_BOARD_CONFIG.copy()
        new_settings.update({'name': 'Hamster'})
        self.dbsession.add(board)
        self.dbsession.commit()
        self.assertEqual(board.settings, new_settings)

    def test_topics(self):
        from ..models import Board, Topic
        board1 = self._make(Board(title="Foobar", slug="foo"))
        board2 = self._make(Board(title="Lorem", slug="lorem"))
        topic1 = self._make(Topic(board=board1, title="Heavenly Moon"))
        topic2 = self._make(Topic(board=board1, title="Beastie Starter"))
        topic3 = self._make(Topic(board=board1, title="Evans"))
        self.dbsession.commit()
        self.assertEqual({topic3, topic2, topic1}, set(board1.topics))
        self.assertEqual([], list(board2.topics))

    def test_topics_sort(self):
        from datetime import datetime, timedelta
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="First"))
        topic2 = self._make(Topic(board=board, title="Second"))
        topic3 = self._make(Topic(board=board, title="Third"))
        topic4 = self._make(Topic(board=board, title="Fourth"))
        topic5 = self._make(Topic(board=board, title="Fifth"))
        self._make(TopicMeta(
            topic=topic1,
            post_count=1,
            bumped_at=datetime.now() + timedelta(minutes=2),
            posted_at=datetime.now() + timedelta(minutes=6)))
        self._make(TopicMeta(
            topic=topic2,
            post_count=1,
            bumped_at=datetime.now() + timedelta(minutes=4),
            posted_at=datetime.now() + timedelta(minutes=6)))
        self._make(TopicMeta(
            topic=topic3,
            post_count=1,
            bumped_at=datetime.now() + timedelta(minutes=3),
            posted_at=datetime.now() + timedelta(minutes=3)))
        self._make(TopicMeta(
            topic=topic5,
            post_count=1,
            bumped_at=datetime.now() + timedelta(minutes=5),
            posted_at=datetime.now() + timedelta(minutes=5)))
        self.dbsession.commit()
        self.assertEqual(
            [topic5, topic2, topic3, topic1, topic4],
            list(board.topics))


class TestTopicModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(title="Foobar", slug="foo"))
        topic = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        topic_meta = self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.assertEqual(topic.board, board)
        self.assertEqual([], list(topic.posts))
        self.assertEqual([topic], list(board.topics))
        self.assertEqual(topic.meta, topic_meta)

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, TopicMeta, Post
        board = self._make(Board(title='Foobar', slug='foo'))
        topic1 = self._make(Topic(board=board, title='Shamshir Dance'))
        topic2 = self._make(Topic(board=board, title='Nyoah Sword Dance'))
        topic_meta1 = self._make(TopicMeta(topic=topic1, post_count=0))
        topic_meta2 = self._make(TopicMeta(topic=topic2, post_count=0))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Lorem ipsum',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Dolor sit amet',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Quas magnam et',
            ip_address='127.0.0.1'))
        self.assertEqual({post2, post1}, set(topic1.posts))
        self.assertEqual({post3}, set(topic2.posts))
        self.dbsession.delete(topic1)
        self.dbsession.commit()
        self.assertTrue(inspect(topic1).was_deleted)
        self.assertFalse(inspect(topic2).was_deleted)
        self.assertTrue(inspect(topic_meta1).was_deleted)
        self.assertFalse(inspect(topic_meta2).was_deleted)
        self.assertTrue(inspect(post1).was_deleted)
        self.assertTrue(inspect(post2).was_deleted)
        self.assertFalse(inspect(post3).was_deleted)

    def test_versioned(self):
        from ..models import Board, Topic
        TopicHistory = Topic.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self.dbsession.commit()
        self.assertEqual(topic.version, 1)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        topic.title = 'Foobar Baz'
        self.dbsession.add(topic)
        self.dbsession.commit()
        self.assertEqual(topic.version, 2)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, topic.board_id)
        self.assertEqual(topic_1.title, 'Foobar')
        self.assertEqual(topic_1.change_type, 'update')
        self.assertEqual(topic_1.version, 1)
        self.assertIsNotNone(topic_1.changed_at)
        self.assertIsNotNone(topic_1.created_at)
        self.assertIsNone(topic_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic
        TopicHistory = Topic.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Foobar'))
        self.dbsession.commit()
        self.dbsession.delete(topic)
        self.dbsession.commit()
        self.assertTrue(inspect(topic).was_deleted)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, topic.board_id)
        self.assertEqual(topic_1.title, 'Foobar')
        self.assertEqual(topic_1.change_type, 'delete')
        self.assertEqual(topic_1.version, 1)

    def test_versioned_deleted_cascade(self):
        from ..models import Board, Topic, Post
        BoardHistory = Board.__history_mapper__.class_
        TopicHistory = Topic.__history_mapper__.class_
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Cosmic Agenda'))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Foobar',
            ip_address='127.0.0.1'))
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 0)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        self.dbsession.delete(topic)
        self.dbsession.commit()
        self.assertEqual(self.dbsession.query(BoardHistory).count(), 0)
        self.assertEqual(self.dbsession.query(TopicHistory).count(), 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        topic_1 = self.dbsession.query(TopicHistory).filter_by(version=1).one()
        self.assertEqual(topic_1.id, topic.id)
        self.assertEqual(topic_1.board_id, board.id)
        self.assertEqual(topic_1.change_type, 'delete')
        self.assertEqual(topic_1.version, 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.change_type, 'delete')
        self.assertEqual(post_1.version, 1)

    def test_posts(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foo"))
        topic1 = self._make(Topic(board=board, title="Lorem ipsum dolor"))
        topic2 = self._make(Topic(board=board, title="Some lonely topic"))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Lorem',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Ipsum',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic1,
            number=3,
            name='Nameless Fanboi',
            body='Dolor',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual([post1, post2, post3], list(topic1.posts))
        self.assertEqual([], list(topic2.posts))

    def test_meta(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Lorem ipsum dolor'))
        self._make(TopicMeta(topic=topic, post_count=0))
        self.dbsession.commit()
        self.assertEqual(topic.meta.post_count, 0)
        self.assertIsNone(topic.meta.posted_at)
        self.assertIsNone(topic.meta.bumped_at)

    def test_scoped_posts(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic = self._make(Topic(board=board, title="Hello, world!"))
        post1 = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Post 1',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic,
            number=2,
            name='Nameless Fanboi',
            body='Post 2',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            number=3,
            topic=topic,
            name='Nameless Fanboi',
            body='Post 3',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertListEqual(topic.scoped_posts(None), [post1, post2, post3])
        self.assertListEqual(topic.scoped_posts("bogus"), [])

    def test_single_post(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another post!!1"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Post 1',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Post 2',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=2,
            name='Nameless Fanboi',
            body='Post 2',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        results = topic1.single_post(2)
        self.assertListEqual(results, [post3])
        self.assertListEqual(results, topic1.scoped_posts("2"))
        self.assertListEqual(topic1.single_post(1000), [])
        self.assertListEqual(topic3.single_post(1), [])
        self.assertListEqual(topic3.single_post(), [])

    def test_ranged_posts(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Topic 1, Post 1',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Topic 1, Post 2',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic1,
            number=3,
            name='Nameless Fanboi',
            body='Topic 1, Post 3',
            ip_address='127.0.0.1'))
        post4 = self._make(Post(
            topic=topic1,
            number=4,
            name='Nameless Fanboi',
            body='Topic 1, Post 4',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Topic 2, Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=2,
            name='Nameless Fanboi',
            body='Topic 2, Post 2',
            ip_address='127.0.0.1'))
        post7 = self._make(Post(
            topic=topic1,
            number=5,
            name='Nameless Fanboi',
            body='Topic 1, Post 5',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        results = topic1.ranged_posts(2, 5)
        self.assertListEqual(results, [post2, post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("2-5"))
        self.assertListEqual(topic1.ranged_posts(1000, 1005), [])
        self.assertListEqual(topic3.ranged_posts(1, 5), [])
        self.assertListEqual(topic1.ranged_posts(), topic1.posts.all())

    def test_ranged_posts_without_end(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Topic 1, Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Topic 1, Post 2',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic1,
            number=3,
            name='Nameless Fanboi',
            body='Topic 1, Post 3',
            ip_address='127.0.0.1'))
        post4 = self._make(Post(
            topic=topic1,
            number=4,
            name='Nameless Fanboi',
            body='Topic 1, Post 4',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Topic 2, Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=2,
            name='Nameless Fanboi',
            body='Topic 2, Post 2',
            ip_address='127.0.0.1'))
        post7 = self._make(Post(
            topic=topic1,
            number=5,
            name='Nameless Fanboi',
            body='Topic 1, Post 5',
            ip_address='127.0.0.1'))
        results = topic1.ranged_posts(3)
        self.assertListEqual(results, [post3, post4, post7])
        self.assertListEqual(results, topic1.scoped_posts("3-"))
        self.assertListEqual(topic1.ranged_posts(1000), [])
        self.assertListEqual(topic3.ranged_posts(3), [])

    def test_range_query_without_start(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic1 = self._make(Topic(board=board, title='Hello, world!'))
        topic2 = self._make(Topic(board=board, title='Another test'))
        topic3 = self._make(Topic(board=board, title='Empty topic'))
        post1 = self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Topic 1, Post 1',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Topic 1, Post 2',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic1,
            number=3,
            name='Nameless Fanboi',
            body='Topic 1, Post 3',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic1,
            number=4,
            name='Nameless Fanboi',
            body='Topic 1, Post 4',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=1,
            name='Nameless Fanboi',
            body='Topic 2, Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic2,
            number=2,
            name='Nameless Fanboi',
            body='Topic 2, Post 2',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic1,
            number=5,
            name='Nameless Fanboi',
            body='Topic 1, Post 5',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        results = topic1.ranged_posts(None, 3)
        self.assertListEqual(results, [post1, post2, post3])
        self.assertListEqual(results, topic1.scoped_posts('-3'))
        self.assertListEqual(topic1.ranged_posts(None, 0), [])
        self.assertListEqual(topic3.ranged_posts(None, 3), [])

    def test_recent_query(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title="Foobar", slug="foobar"))
        topic1 = self._make(Topic(board=board, title="Hello, world!"))
        topic2 = self._make(Topic(board=board, title="Another test"))
        topic3 = self._make(Topic(board=board, title="Empty topic"))
        self._make(Post(
            topic=topic1,
            number=1,
            name='Nameless Fanboi',
            body='Topic 1, Post 1',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic1,
            number=2,
            name='Nameless Fanboi',
            body='Topic 1, Post 2',
            ip_address='127.0.0.1'))
        for i in range(5):
            self._make(Post(
                topic=topic2,
                number=i+1,
                name='Nameless Fanboi',
                body='Foobar',
                ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic2,
            number=6,
            name='Nameless Fanboi',
            body='Topic 2, Post 6',
            ip_address='127.0.0.1'))
        self._make(Post(
            topic=topic1,
            number=3,
            name='Nameless Fanboi',
            body='Topic 1, Post 3',
            ip_address='127.0.0.1'))
        for i in range(24):
            self._make(Post(
                topic=topic2,
                number=i+7,
                name='Nameless Fanboi',
                body='Foobar',
                ip_address='127.0.0.1'))
        post5 = self._make(Post(
            topic=topic2,
            number=31,
            name='Nameless Fanboi',
            body='Topic 2, Post 31',
            ip_address='127.0.0.1'))
        for i in range(3):
            self._make(Post(
                topic=topic2,
                number=i + 32,
                name='Nameless Fanboi',
                body='Foobar',
                ip_address='127.0.0.1'))
        post6 = self._make(Post(
            topic=topic2,
            number=35,
            name='Nameless Fanboi',
            body='Topic 2, Post 35',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
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
        from ..models import Board, Topic, Post
        board = self._make(Board(title='Foobar', slug='foobar'))
        topic = self._make(Topic(board=board, title='Hello, world!'))
        post1 = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Post 1',
            ip_address='127.0.0.1'))
        post2 = self._make(Post(
            topic=topic,
            number=2,
            name='Nameless Fanboi',
            body='Post 2',
            ip_address='127.0.0.1'))
        post3 = self._make(Post(
            topic=topic,
            number=3,
            name='Nameless Fanboi',
            body='Post 3',
            ip_address='127.0.0.1'))
        post4 = self._make(Post(
            topic=topic,
            number=4,
            name='Nameless Fanboi',
            body='Post 4',
            ip_address='127.0.0.1'))
        post5 = self._make(Post(
            topic=topic,
            number=5,
            name='Nameless Fanboi',
            body='Post 5',
            ip_address='127.0.0.1'))
        post6 = self._make(Post(
            topic=topic,
            number=6,
            name='Nameless Fanboi',
            body='Post 6',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertListEqual(
            [post2, post3, post4, post5, post6],
            topic.scoped_posts('l5'))
        self.dbsession.delete(post3)
        self.dbsession.commit()
        self.assertListEqual(
            [post1, post2, post4, post5, post6],
            topic.scoped_posts('l5'))


class TestTopicMetaModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from ..models import Board, Topic, TopicMeta
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Lorem ipsum dolor sit'))
        topic_meta = self._make(TopicMeta(topic=topic, post_count=1))
        self.dbsession.commit()
        self.assertEqual(topic_meta.topic, topic)
        self.assertEqual(topic_meta, topic.meta)


class TestPostModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from ..models import Board, Topic, Post
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Lorem ipsum dolor sit'))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Hello, world',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(post.topic, topic)
        self.assertEqual([post], list(topic.posts))

    def test_versioned(self):
        from ..models import Board, Topic, Post
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Lorem ipsum dolor'))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Foobar baz',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(post.version, 1)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 0)
        post.body = 'Foobar baz updated'
        self.dbsession.add(post)
        self.dbsession.commit()
        self.assertEqual(post.version, 2)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.body, 'Foobar baz')
        self.assertEqual(post_1.version, 1)
        self.assertIsNotNone(post_1.changed_at)
        self.assertIsNotNone(post_1.created_at)
        self.assertIsNone(post_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Board, Topic, Post
        PostHistory = Post.__history_mapper__.class_
        board = self._make(Board(title='Foobar', slug='foo'))
        topic = self._make(Topic(board=board, title='Lorem ipsum dolor'))
        post = self._make(Post(
            topic=topic,
            number=1,
            name='Nameless Fanboi',
            body='Foobar baz',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.dbsession.delete(post)
        self.dbsession.commit()
        self.assertTrue(inspect(post).was_deleted)
        self.assertEqual(self.dbsession.query(PostHistory).count(), 1)
        post_1 = self.dbsession.query(PostHistory).filter_by(version=1).one()
        self.assertEqual(post_1.id, post.id)
        self.assertEqual(post_1.topic_id, topic.id)
        self.assertEqual(post_1.body, 'Foobar baz')
        self.assertEqual(post_1.change_type, 'delete')
        self.assertEqual(post_1.version, 1)


class TestPageModel(ModelSessionMixin, unittest.TestCase):

    def test_versioned(self):
        from ..models import Page
        PageHistory = Page.__history_mapper__.class_
        page = self._make(Page(title='Foo', slug='foo', body='Foobar'))
        self.dbsession.commit()
        self.assertEqual(page.version, 1)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 0)
        page.body = 'Foobar baz updated'
        self.dbsession.add(page)
        self.dbsession.commit()
        self.assertEqual(page.version, 2)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 1)
        page_1 = self.dbsession.query(PageHistory).filter_by(version=1).one()
        self.assertEqual(page_1.id, page.id)
        self.assertEqual(page_1.title, 'Foo')
        self.assertEqual(page_1.slug, 'foo')
        self.assertEqual(page_1.body, 'Foobar')
        self.assertEqual(page_1.version, 1)
        self.assertEqual(page_1.change_type, 'update')
        self.assertIsNotNone(page_1.changed_at)
        self.assertIsNotNone(page_1.created_at)
        self.assertIsNone(page_1.updated_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Page
        PageHistory = Page.__history_mapper__.class_
        page = self._make(Page(title='Foo', slug='foo', body='Foobar'))
        self.dbsession.commit()
        self.dbsession.delete(page)
        self.dbsession.commit()
        self.assertTrue(inspect(page).was_deleted)
        self.assertEqual(self.dbsession.query(PageHistory).count(), 1)
        page_1 = self.dbsession.query(PageHistory).filter_by(version=1).one()
        self.assertEqual(page_1.id, page.id)
        self.assertEqual(page_1.title, 'Foo')
        self.assertEqual(page_1.slug, 'foo')
        self.assertEqual(page_1.body, 'Foobar')
        self.assertEqual(page_1.version, 1)
        self.assertEqual(page_1.change_type, 'delete')
        self.assertIsNotNone(page_1.changed_at)
        self.assertIsNotNone(page_1.created_at)
        self.assertIsNone(page_1.updated_at)


class TestRuleModel(ModelSessionMixin, unittest.TestCase):

    def test_inheritance(self):
        from ..models import Rule, RuleBan
        rule = self._make(Rule(ip_address='127.0.0.1'))
        rule_ban = self._make(RuleBan(ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertListEqual(
            list(self.dbsession.query(Rule).order_by(Rule.id).all()),
            [rule, rule_ban])

    def test_listed(self):
        from datetime import datetime, timedelta
        from ..models import Rule
        rule1 = self._make(Rule(ip_address='10.0.1.0/24'))
        rule2 = self._make(Rule(ip_address='10.0.2.0/24'))
        rule3 = self._make(Rule(ip_address='10.0.3.1'))
        rule4 = self._make(Rule(ip_address='10.0.4.0/24', scope='foo:bar'))
        self._make(Rule(ip_address='10.0.5.0/24', active=False))
        self._make(Rule(
            ip_address='10.0.6.0/24',
            active_until=datetime.now() - timedelta(days=1)))
        self.dbsession.commit()

        def _makeQuery(ip_address, **kwargs):
            return self.dbsession.query(Rule).filter(
                Rule.listed(ip_address, **kwargs)).first()
        self.assertEqual(rule1, _makeQuery('10.0.1.1'))
        self.assertEqual(rule2, _makeQuery('10.0.2.1'))
        self.assertEqual(rule3, _makeQuery('10.0.3.1'))
        self.assertEqual(rule3, _makeQuery('10.0.3.1', scopes=['foo:bar']))
        self.assertEqual(rule4, _makeQuery('10.0.4.1', scopes=['foo:bar']))
        self.assertEqual(None, _makeQuery('10.0.4.1'))
        self.assertEqual(None, _makeQuery('10.0.5.1'))
        self.assertEqual(None, _makeQuery('10.0.6.1'))

    def test_duration(self):
        from datetime import datetime, timedelta
        from ..models import Rule
        rule = self._make(Rule(
            ip_address='10.0.1.0/24',
            active_until=datetime.now() + timedelta(days=30)))
        self.dbsession.commit()
        self.assertEqual(rule.duration, 30)

    def test_duration_no_duration(self):
        from ..models import Rule
        rule = self._make(Rule(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        self.assertEqual(rule.duration, 0)


class TestRuleBanModel(ModelSessionMixin, unittest.TestCase):

    def test_inheritance(self):
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(rule_ban.type, 'ban')
        self.assertEqual(rule_ban.ip_address, '127.0.0.1')

    def test_listed(self):
        from datetime import datetime, timedelta
        from ..models import Rule, RuleBan
        rule_ban1 = self._make(RuleBan(ip_address='10.0.1.0/24'))
        rule_ban2 = self._make(RuleBan(ip_address='10.0.2.0/24'))
        rule_ban3 = self._make(RuleBan(ip_address='10.0.3.1'))
        rule_ban4 = self._make(RuleBan(
            ip_address='10.0.4.0/24',
            scope='foo:bar'))
        self._make(Rule(ip_address='10.0.5.0/24'))
        self._make(RuleBan(ip_address='10.0.7.0/24', active=False))
        self._make(RuleBan(
            ip_address='10.0.8.0/24',
            active_until=datetime.now() - timedelta(days=1)))
        self.dbsession.commit()

        def _makeQuery(ip_address, **kwargs):
            return self.dbsession.query(RuleBan).\
                filter(RuleBan.listed(ip_address, **kwargs)).first()
        self.assertEqual(rule_ban1, _makeQuery('10.0.1.1'))
        self.assertEqual(rule_ban2, _makeQuery('10.0.2.1'))
        self.assertEqual(rule_ban3, _makeQuery('10.0.3.1'))
        self.assertEqual(rule_ban3, _makeQuery('10.0.3.1', scopes=['foo:bar']))
        self.assertEqual(rule_ban4, _makeQuery('10.0.4.1', scopes=['foo:bar']))
        self.assertEqual(None, _makeQuery('10.0.4.1'))
        self.assertEqual(None, _makeQuery('10.0.5.1'))
        self.assertEqual(None, _makeQuery('10.0.6.1'))
        self.assertEqual(None, _makeQuery('10.0.7.1'))
        self.assertEqual(None, _makeQuery('10.0.8.1'))

    def test_duration(self):
        from datetime import datetime, timedelta
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(
            ip_address='10.0.1.0/24',
            active_until=datetime.now() + timedelta(days=30)))
        self.dbsession.commit()
        self.assertEqual(rule_ban.duration, 30)

    def test_duration_no_duration(self):
        from ..models import RuleBan
        rule_ban = self._make(RuleBan(ip_address='10.0.1.0/24'))
        self.dbsession.commit()
        self.assertEqual(rule_ban.duration, 0)


class TestSettingModel(ModelSessionMixin, unittest.TestCase):

    def test_versioned(self):
        from ..models import Setting
        SettingHistory = Setting.__history_mapper__.class_
        setting = self._make(Setting(key='foo', value='bar'))
        self.dbsession.commit()
        self.assertEqual(setting.version, 1)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 0)
        setting.value = 'baz'
        self.dbsession.add(setting)
        self.dbsession.commit()
        self.assertEqual(setting.version, 2)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 1)
        setting_1 = self.dbsession.query(SettingHistory).\
            filter_by(version=1).\
            one()
        self.assertEqual(setting_1.key, 'foo')
        self.assertEqual(setting_1.value, 'bar')
        self.assertEqual(setting_1.version, 1)
        self.assertEqual(setting_1.change_type, 'update')
        self.assertIsNotNone(setting_1.changed_at)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from ..models import Setting
        SettingHistory = Setting.__history_mapper__.class_
        setting = self._make(Setting(key='foo', value='bar'))
        self.dbsession.commit()
        self.dbsession.delete(setting)
        self.dbsession.commit()
        self.assertTrue(inspect(setting).was_deleted)
        self.assertEqual(self.dbsession.query(SettingHistory).count(), 1)
        setting_1 = self.dbsession.query(SettingHistory).\
            filter_by(version=1).\
            one()
        self.assertEqual(setting_1.key, 'foo')
        self.assertEqual(setting_1.value, 'bar')
        self.assertEqual(setting_1.version, 1)
        self.assertEqual(setting_1.change_type, 'delete')
        self.assertIsNotNone(setting_1.changed_at)


class TestUserModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='foo1',
            parent=user1,
            encrypted_password='none',
            groups=[group1]))
        user3 = self._make(User(
            username='foo2',
            parent=user1,
            encrypted_password='none',
            groups=[group2]))
        user4 = self._make(User(
            username='foo3',
            parent=user2,
            encrypted_password='none'))
        session1 = self._make(UserSession(
            user=user1,
            token='test1',
            ip_address='127.0.0.1',
            created_at=datetime.now() - timedelta(days=1)))
        session2 = self._make(UserSession(
            user=user1,
            token='test2',
            ip_address='127.0.0.1'))
        session3 = self._make(UserSession(
            user=user2,
            token='test3',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(list(user1.children), [user2, user3])
        self.assertEqual(list(user2.children), [user4])
        self.assertEqual(list(user3.children), [])
        self.assertEqual(list(user4.children), [])
        self.assertEqual(list(user1.sessions), [session2, session1])
        self.assertEqual(list(user2.sessions), [session3])
        self.assertEqual(list(user3.sessions), [])
        self.assertEqual(list(user4.sessions), [])
        self.assertEqual(list(user1.groups), [group2, group1])
        self.assertEqual(list(user2.groups), [group1])
        self.assertEqual(list(user3.groups), [group2])
        self.assertEqual(list(user4.groups), [])
        self.assertIsNone(user1.parent)
        self.assertEqual(user2.parent, user1)
        self.assertEqual(user3.parent, user1)

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import User, UserSession, Group
        group1 = self._make(Group(name='foo1'))
        group2 = self._make(Group(name='foo2'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='none',
            groups=[group1]))
        user2 = self._make(User(
            username='foo1',
            parent=user1,
            encrypted_password='none',
            groups=[group2]))
        user3 = self._make(User(
            username='foo2',
            parent=user1,
            encrypted_password='none'))
        user4 = self._make(User(
            username='foo3',
            parent=user2,
            encrypted_password='none'))
        session1 = self._make(UserSession(
            user=user1,
            token='test1',
            ip_address='127.0.0.1'))
        session2 = self._make(UserSession(
            user=user2,
            token='test2',
            ip_address='127.0.0.1'))
        session3 = self._make(UserSession(
            user=user2,
            token='test3',
            ip_address='127.0.0.1'))
        session4 = self._make(UserSession(
            user=user3,
            token='test4',
            ip_address='127.0.0.1'))
        session5 = self._make(UserSession(
            user=user4,
            token='test5',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.dbsession.delete(user2)
        self.dbsession.commit()
        self.assertTrue(inspect(user2).was_deleted)
        self.assertTrue(inspect(user4).was_deleted)
        self.assertTrue(inspect(session2).was_deleted)
        self.assertTrue(inspect(session3).was_deleted)
        self.assertTrue(inspect(session5).was_deleted)
        self.assertFalse(inspect(user1).was_deleted)
        self.assertFalse(inspect(user3).was_deleted)
        self.assertFalse(inspect(group1).was_deleted)
        self.assertFalse(inspect(group2).was_deleted)
        self.assertFalse(inspect(session1).was_deleted)
        self.assertFalse(inspect(session4).was_deleted)


class TestUserSessionModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from datetime import datetime, timedelta
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none'))
        session1 = self._make(UserSession(
            user=user,
            token='test1',
            ip_address='127.0.0.1',
            created_at=datetime.now() - timedelta(days=1)))
        session2 = self._make(UserSession(
            user=user,
            token='test2',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.assertEqual(session1.user, user)
        self.assertEqual(session2.user, user)
        self.assertEqual(list(user.sessions), [session2, session1])

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import User, UserSession
        user = self._make(User(
            username='foo',
            encrypted_password='none'))
        session = self._make(UserSession(
            user=user,
            token='test1',
            ip_address='127.0.0.1'))
        self.dbsession.commit()
        self.dbsession.delete(session)
        self.dbsession.commit()
        self.assertTrue(inspect(session).was_deleted)
        self.assertFalse(inspect(user).was_deleted)


class TestGroupModel(ModelSessionMixin, unittest.TestCase):

    def test_relations(self):
        from ..models import Group, User
        group1 = self._make(Group(name='foo'))
        group2 = self._make(Group(name='bar'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='dummy',
            groups=[group1, group2]))
        user2 = self._make(User(
            username='foo2',
            encrypted_password='dummy',
            groups=[group1]))
        user3 = self._make(User(
            username='foo3',
            encrypted_password='dummy',
            groups=[group2]))
        self.dbsession.commit()
        self.assertEqual(list(group1.users), [user1, user2])
        self.assertEqual(list(group2.users), [user1, user3])

    def test_relations_cascade(self):
        from sqlalchemy import inspect
        from ..models import Group, User
        group = self._make(Group(name='foo'))
        user1 = self._make(User(
            username='foo',
            encrypted_password='dummy',
            groups=[group]))
        user2 = self._make(User(
            username='foo2',
            encrypted_password='dummy',
            groups=[group]))
        self.dbsession.commit()
        self.dbsession.delete(group)
        self.dbsession.commit()
        self.assertTrue(inspect(group).was_deleted)
        self.assertFalse(inspect(user1).was_deleted)
        self.assertFalse(inspect(user2).was_deleted)
