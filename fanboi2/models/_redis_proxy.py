import redis


class RedisProxy(object):
    """Wrapper around :class:`redis.StrictRedis` to allow late binding of
    Redis object. This wrapper will proxy all method calls to Redis object
    if initialized.
    """

    def __init__(self, cls=redis.StrictRedis):
        self._cls = cls
        self._redis = None

    def from_url(self, *args, **kwargs):
        self._redis = self._cls.from_url(*args, **kwargs)

    def __getattr__(self, name):
        if self._redis is not None:
            return self._redis.__getattribute__(name)
        raise RuntimeError("{} is not initialized".
                           format(repr(self._cls.__name__)))
