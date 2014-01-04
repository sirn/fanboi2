import os
import transaction
from fanboi2.models import DBSession, Base, redis_conn
from pyramid import testing
from sqlalchemy import create_engine


DATABASE_URI = os.environ.get(
    'POSTGRESQL_TEST_DATABASE',
    'postgresql://fanboi2:fanboi2@localhost:5432/fanboi2_test')


class DummyRedis(object):

    @classmethod
    def from_url(cls, *args, **kwargs):
        return cls()

    def __init__(self):
        self._store = {}
        self._expire = {}

    def get(self, key):
        return self._store.get(key, None)

    def set(self, key, value):
        try:
            value = bytes(value.encode('utf-8'))
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

    def ping(self):
        return True


class _ModelInstanceSetup(object):

    def _makeBoard(self, **kwargs):
        from fanboi2.models import Board
        board = Board(**kwargs)
        DBSession.add(board)
        DBSession.flush()
        return board

    def _makeTopic(self, **kwargs):
        from fanboi2.models import Topic
        topic = Topic(**kwargs)
        DBSession.add(topic)
        DBSession.flush()
        return topic

    def _makePost(self, **kwargs):
        from fanboi2.models import Post
        if not kwargs.get('ip_address', None):
            kwargs['ip_address'] = '0.0.0.0'
        post = Post(**kwargs)
        DBSession.add(post)
        DBSession.flush()
        return post


class ModelMixin(_ModelInstanceSetup):

    @classmethod
    def tearDownClass(cls):
        Base.metadata.bind = None
        DBSession.remove()

    @classmethod
    def setUpClass(cls):
        engine = create_engine(DATABASE_URI)
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

    def setUp(self):
        redis_conn._redis = DummyRedis()
        Base.metadata.drop_all()
        Base.metadata.create_all()
        transaction.begin()
        self.request = self._makeRequest()
        self.registry = self._makeRegistry()
        self.config = testing.setUp(
            request=self.request,
            registry=self.registry)

    def tearDown(self):
        redis_conn._redis = None
        testing.tearDown()
        transaction.abort()

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.user_agent = 'Mock/1.0'
        request.referrer = None
        return request

    def _makeRegistry(self):
        from pyramid.registry import Registry
        registry = Registry()
        registry.settings = {
            'app.timezone': 'Asia/Bangkok',
            'app.secret': 'Silently test in secret',
            }
        return registry


class TaskMixin(object):

    @classmethod
    def setUpClass(cls):
        from fanboi2.tasks import celery
        celery.config_from_object({'CELERY_ALWAYS_EAGER': True})
        super(TaskMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        from fanboi2.tasks import celery
        celery.config_from_object({'CELERY_ALWAYS_EAGER': False})
        super(TaskMixin, cls).tearDownClass()


class ViewMixin(object):

    def _make_csrf(self, request):
        import hmac
        import os
        from hashlib import sha1
        request.session['csrf'] = sha1(os.urandom(64)).hexdigest()
        request.params['csrf_token'] = hmac.new(
            bytes(request.registry.settings['app.secret'].encode('utf8')),
            bytes(request.session['csrf'].encode('utf8')),
            digestmod=sha1,
            ).hexdigest()
        return request

    def _POST(self, data=None):
        from webob.multidict import MultiDict
        request = self.request
        request.method = 'POST'
        request.remote_addr = "127.0.0.1"
        request.params = MultiDict(data)
        return request

    def _GET(self, data=None):
        from webob.multidict import MultiDict
        request = self.request
        if data is None:
            data = {}
        request.remote_addr = "127.0.0.1"
        request.params = MultiDict(data)
        return request


class CacheMixin(object):

    def _getRegion(self, store=None):
        from dogpile.cache import make_region
        return make_region().configure('dogpile.cache.memory', arguments={
            'cache_dict': store if store is not None else {},
            })
