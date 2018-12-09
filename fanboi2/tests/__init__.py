import datetime
import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from pyramid import testing

from ..models import make_history_event


DATABASE_URL = os.environ.get(
    "POSTGRESQL_TEST_DATABASE", "postgresql://fanboi2:@localhost:5432/fanboi2_test"
)

engine = create_engine(DATABASE_URL)
dbmaker = sessionmaker()
make_history_event(dbmaker)


def make_cache_region(store=None):
    from dogpile.cache import make_region

    if store is None:
        store = {}
    return make_region().configure(
        "dogpile.cache.memory", arguments={"cache_dict": store}
    )


def mock_service(request, mappings):
    def _find_service(iface=None, name=None):
        for l in (iface, name):
            if l in mappings:
                return mappings[l]

    request.find_service = _find_service
    return request


class DummyRedis(object):
    def __init__(self, time=None):
        self._reset()
        self._set_time(time)

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        try:
            value = bytes(value.encode("utf-8"))
        except AttributeError:
            pass
        self._store[key] = value

    def setnx(self, key, value):
        if not self.get(key):
            self.set(key, value)

    def exists(self, key):
        return key in self._store

    def expire(self, key, time):
        self._expire[key] = time

    def ttl(self, key):
        return self._expire.get(key, 0)

    def time(self):
        ts = self._time.timestamp()
        return (int(ts), int((ts - int(ts)) * 1000000))

    def _reset(self):
        self._store = {}
        self._expire = {}

    def _set_time(self, time=None):
        if not time:
            time = datetime.datetime.now()
        self._time = time


class DummyAsyncResult(object):
    def __init__(self, id_, status, result=None):
        self._id = id_
        self._status = status
        self._result = result

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status.upper()

    @property
    def state(self):
        from celery import states

        return getattr(states, self.status)

    def get(self):
        return self._result


class ModelTransactionEngineMixin(object):
    def setUp(self):
        super(ModelTransactionEngineMixin, self).setUp()
        self.connection = engine.connect()
        self.tx = self.connection.begin()

    def tearDown(self):
        super(ModelTransactionEngineMixin, self).tearDown()
        self.tx.rollback()
        self.connection.close()


class ModelSessionMixin(ModelTransactionEngineMixin, object):
    def setUp(self):
        super(ModelSessionMixin, self).setUp()
        from sqlalchemy import event
        from ..models import Base

        self.dbsession = dbmaker(bind=self.connection)
        Base.metadata.bind = self.connection
        Base.metadata.create_all()
        self.dbsession.begin_nested()

        @event.listens_for(self.dbsession, "after_transaction_end")
        def restart_savepoint(dbsession, transaction):
            if transaction.nested and not transaction._parent.nested:
                dbsession.expire_all()
                dbsession.begin_nested()

    def tearDown(self):
        super(ModelSessionMixin, self).tearDown()
        self.dbsession.close()

    def _make(self, model_obj):
        self.dbsession.add(model_obj)
        return model_obj


class IntegrationMixin(ModelSessionMixin, object):
    def setUp(self):
        super(IntegrationMixin, self).setUp()
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = self.config.registry
        self.request.user_agent = "Mock/1.0"
        self.request.client_addr = "127.0.0.1"
        self.request.referrer = "https://www.example.com/referer"
        self.request.url = "https://www.example.com/url"
        self.request.application_url = "https://www.example.com"

    def tearDown(self):
        super(IntegrationMixin, self).tearDown()
        testing.tearDown()
