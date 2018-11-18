import unittest

from sqlalchemy.ext.declarative import declarative_base

from . import ModelTransactionEngineMixin


class TestDeserializeModel(unittest.TestCase):
    def test_serialize(self):
        from ..models import deserialize_model
        from ..models import (
            Ban,
            Banword,
            Board,
            Group,
            Page,
            Post,
            Setting,
            Topic,
            TopicMeta,
            User,
            UserSession,
        )

        self.assertEqual(deserialize_model("ban"), Ban)
        self.assertEqual(deserialize_model("banword"), Banword)
        self.assertEqual(deserialize_model("board"), Board)
        self.assertEqual(deserialize_model("group"), Group)
        self.assertEqual(deserialize_model("page"), Page)
        self.assertEqual(deserialize_model("post"), Post)
        self.assertEqual(deserialize_model("setting"), Setting)
        self.assertEqual(deserialize_model("topic"), Topic)
        self.assertEqual(deserialize_model("topic_meta"), TopicMeta)
        self.assertEqual(deserialize_model("user"), User)
        self.assertEqual(deserialize_model("user_session"), UserSession)
        self.assertIsNone(deserialize_model("foo"))


class TestBaseModel(unittest.TestCase):
    def _get_target_class(self):
        from sqlalchemy import Column, Integer
        from ..models._base import BaseModel

        MockBase = declarative_base()

        class MockModel(BaseModel, MockBase):
            __tablename__ = "mock"
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
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            body = Column(String)
            created_at = Column(DateTime(timezone=True), default=func.now())

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(body="Hello, world")
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.body = "Hello, galaxy"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.body, "Hello, world")
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)
        self.assertIsNotNone(thing_1.created_at)
        thing.body = "Hello, universe"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_2.body, "Hello, galaxy")
        self.assertEqual(thing_2.change_type, "update")
        self.assertEqual(thing_2.version, 2)
        self.assertIsNotNone(thing_2.changed_at)
        self.assertIsNotNone(thing_2.created_at)

    def test_versioned_column(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            ref = Column(String, unique=True, info={"version_meta": True})

        self._get_setup_function(mappers)(self.dbsession)
        thing_history_table = Thing.__history_mapper__.local_table
        self.assertIsNone(getattr(thing_history_table.c, "ref", None))

    def test_versioned_null(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
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
        thing.body = "Hello, world"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertIsNone(thing_1.body)
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)
        thing.body = None
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual("Hello, world", thing_2.body)
        self.assertEqual(thing_2.change_type, "update")
        self.assertEqual(thing_2.version, 2)
        self.assertIsNotNone(thing_2.changed_at)

    def test_versioned_bool(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, Boolean

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
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
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)

    def test_versioned_deferred(self):
        from sqlalchemy.orm import deferred
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            name = Column(String, default=False)
            data = deferred(Column(String))

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(name="test", data="Hello, world")
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.dbsession.commit()
        thing = self.dbsession.query(Thing).first()
        thing.data = "Hello, galaxy"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, "Hello, world")
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        self.assertIsNotNone(thing_1.changed_at)

    def test_versioned_inheritance(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"

            id = Column(Integer, primary_key=True)
            name = Column(String)
            type = Column(String)

            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "base"}

        class ThingSeparatePk(Thing):
            __tablename__ = "thing_separate_pk"
            __mapper_args__ = {"polymorphic_identity": "separate_pk"}

            id = column_property(Column(Integer, primary_key=True), Thing.id)
            thing_id = Column(Integer, ForeignKey("thing.id"))
            sub_data_1 = Column(String)

        class ThingSamePk(Thing):
            __tablename__ = "thing_same_pk"
            __mapper_args__ = {"polymorphic_identity": "same_pk"}

            id = Column(Integer, ForeignKey("thing.id"), primary_key=True)
            sub_data_2 = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSeparatePkHistory = ThingSeparatePk.__history_mapper__.class_
        ThingSamePkHistory = ThingSamePk.__history_mapper__.class_
        thing = Thing(name="Foo")
        thing_sp = ThingSeparatePk(name="Bar", sub_data_1="Hello, world")
        thing_sm = ThingSamePk(name="Baz", sub_data_2="Hello, galaxy")
        self.dbsession.add_all([thing, thing_sp, thing_sm])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sp.version, 1)
        self.assertEqual(thing_sm.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSeparatePkHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 0)
        thing.name = "Hoge"
        thing_sp.sub_data_1 = "Hello, universe"
        thing_sm.sub_data_2 = "Hello, multiuniverse"
        self.dbsession.add_all([thing, thing_sp, thing_sm])
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 2)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 3)
        self.assertEqual(self.dbsession.query(ThingSeparatePkHistory).count(), 1)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 1)
        thing_sp.sub_data_1 = "Hello, parallel universe"
        self.dbsession.add(thing_sp)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 4)
        self.assertEqual(self.dbsession.query(ThingSeparatePkHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 1)
        thing_sm.sub_data_2 = "Hello, 42"
        self.dbsession.add(thing_sm)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sp.version, 3)
        self.assertEqual(thing_sm.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 5)
        self.assertEqual(self.dbsession.query(ThingSeparatePkHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSamePkHistory).count(), 2)

    def test_versioned_inheritance_multi(self):
        from sqlalchemy.orm import column_property
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"

            id = Column(Integer, primary_key=True)
            name = Column(String)
            type = Column(String)

            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "base"}

        class ThingSub(Thing):
            __tablename__ = "thing_sub"
            __mapper_args__ = {"polymorphic_identity": "sub"}

            id = column_property(Column(Integer, primary_key=True), Thing.id)
            base_id = Column(Integer, ForeignKey("thing.id"))
            sub_data_1 = Column(String)

        class ThingSubSub(ThingSub):
            __tablename__ = "thing_sub_sub"
            __mapper_args__ = {"polymorphic_identity": "sub_sub"}

            id = Column(Integer, ForeignKey("thing_sub.id"), primary_key=True)
            sub_data_2 = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        ThingSubSubHistory = ThingSubSub.__history_mapper__.class_
        thing = Thing(name="Foo")
        thing_sub = ThingSub(name="Bar", sub_data_1="Hello, world")
        thing_sub_sub = ThingSubSub(name="Baz", sub_data_2="Hello, galaxy")
        self.dbsession.add_all([thing, thing_sub, thing_sub_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(thing_sub_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 0)
        thing.name = "Hoge"
        thing_sub.sub_data_1 = "Hello, universe"
        thing_sub_sub.sub_data_2 = "Hello, multiuniverse"
        self.dbsession.add_all([thing, thing_sub, thing_sub_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 3)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 1)
        thing_sub.sub_data_1 = "Hello, parallel universe"
        self.dbsession.add(thing_sub)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 3)
        self.assertEqual(thing_sub_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 4)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 3)
        self.assertEqual(self.dbsession.query(ThingSubSubHistory).count(), 1)
        thing_sub_sub.sub_data_2 = "Hello, 42"
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
            __tablename__ = "thing"

            id = Column(Integer, primary_key=True)
            data = Column(String)
            type = Column(String)

            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "base"}

        class ThingSub(Thing):
            __mapper_args__ = {"polymorphic_identity": "sub"}
            sub_data = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        ThingSubHistory = ThingSub.__history_mapper__.class_
        thing = Thing(data="Hello, world")
        thing_sub = ThingSub(data="Hello, galaxy", sub_data="Hello, universe")
        self.dbsession.add_all([thing, thing_sub])
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        thing.data = "Hello, multiuniverse"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 0)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, "Hello, world")
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        thing_sub.sub_data = "Hello, parallel universe"
        self.dbsession.add(thing_sub)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(thing_sub.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        self.assertEqual(self.dbsession.query(ThingSubHistory).count(), 1)
        thing_sub_1 = self.dbsession.query(ThingSubHistory).filter_by(version=1).one()
        self.assertEqual(thing_sub_1.sub_data, "Hello, universe")
        self.assertEqual(thing_sub_1.change_type, "update")
        self.assertEqual(thing_sub_1.version, 1)

    def test_versioned_unique(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"

            id = Column(Integer, primary_key=True)
            name = Column(String, unique=True)
            data = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(name="Hello", data="Hello, world")
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.data = "Hello, galaxy"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing.data = "Hello, universe"
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
            __tablename__ = "relate"
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey("relate.id"))
            relate = relationship("Relate", backref="things")

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
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
        thing.relate = None
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertIsNone(thing.relate_id)
        self.assertEqual(thing.version, 3)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 2)
        thing_2 = self.dbsession.query(ThingHistory).filter_by(version=2).one()
        self.assertEqual(thing_2.relate_id, relate.id)
        self.assertEqual(thing_2.change_type, "update")
        self.assertEqual(thing_2.version, 2)

    def test_versioned_relationship_cascade_null(self):
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer

        mappers = []
        base = self._make_base()

        class Relate(base):
            __tablename__ = "relate"
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey("relate.id"))
            relate = relationship("Relate", backref="things")

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
        self.assertEqual(thing_1.change_type, "update.cascade")
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
            __tablename__ = "relate"
            id = Column(Integer, primary_key=True)

        class Thing(versioned, base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey("relate.id"))
            relate = relationship("Relate", backref="things")

        class Child(versioned, base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            thing_id = Column(Integer, ForeignKey("thing.id"))
            thing = relationship("Thing", backref="children")

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
        self.assertEqual(thing_1.change_type, "delete")
        self.assertEqual(thing_1.version, 1)
        child_1 = self.dbsession.query(ChildHistory).filter_by(version=1).one()
        self.assertEqual(child_1.thing_id, thing.id)
        self.assertEqual(child_1.change_type, "update.cascade")
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
            __tablename__ = "relate"
            id = Column(Integer, primary_key=True)

        class Thing(versioned, base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey("relate.id"))
            relate = relationship("Relate", backref=backref("things", cascade="all"))

        class Entity(versioned, base):
            __tablename__ = "entity"
            id = Column(Integer, primary_key=True)
            thing_id = Column(Integer, ForeignKey("thing.id"))
            thing = relationship("Thing", backref=backref("entities", cascade="all"))

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
        self.assertEqual(thing_1.change_type, "delete")
        self.assertEqual(thing_1.version, 1)
        entity_1 = self.dbsession.query(EntityHistory).filter_by(version=1).one()
        self.assertEqual(entity_1.thing_id, thing.id)
        self.assertEqual(entity_1.change_type, "delete")
        self.assertEqual(entity_1.version, 1)

    def test_versioned_relationship_cascade_orphan(self):
        from sqlalchemy import inspect
        from sqlalchemy.orm import relationship, backref
        from sqlalchemy.sql.schema import Column, ForeignKey
        from sqlalchemy.sql.sqltypes import Integer

        mappers = []
        base = self._make_base()

        class Relate(base):
            __tablename__ = "relate"
            id = Column(Integer, primary_key=True)

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            relate_id = Column(Integer, ForeignKey("relate.id"))
            relate = relationship(
                "Relate", backref=backref("things", cascade="all,delete-orphan")
            )

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
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)

    def test_versioned_deleted(self):
        from sqlalchemy import inspect
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            data = Column(String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(data="Hello, world")
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        self.dbsession.delete(thing)
        self.dbsession.commit()
        self.assertTrue(inspect(thing).was_deleted)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data, "Hello, world")
        self.assertEqual(thing_1.change_type, "delete")
        self.assertEqual(thing_1.version, 1)

    def test_versioned_named_column(self):
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.sqltypes import Integer, String

        mappers = []
        base = self._make_base()

        class Thing(self._get_target_class(mappers), base):
            __tablename__ = "thing"
            id = Column(Integer, primary_key=True)
            data_ = Column("data", String)

        self._get_setup_function(mappers)(self.dbsession)
        base.metadata.create_all()
        ThingHistory = Thing.__history_mapper__.class_
        thing = Thing(data_="Hello, world")
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 1)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 0)
        thing.data_ = "Hello, galaxy"
        self.dbsession.add(thing)
        self.dbsession.commit()
        self.assertEqual(thing.version, 2)
        self.assertEqual(self.dbsession.query(ThingHistory).count(), 1)
        thing_1 = self.dbsession.query(ThingHistory).filter_by(version=1).one()
        self.assertEqual(thing_1.data_, "Hello, world")
        self.assertEqual(thing_1.change_type, "update")
        self.assertEqual(thing_1.version, 1)
