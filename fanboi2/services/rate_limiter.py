class RateLimiterService(object):
    """Rate limiter service provides a service for querying whether
    the user given by a payload should be rate-limited.
    """

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def _get_key(self, **kwargs):
        return "services.rate_limiter:%s" % (
            (",".join("%s=%s" % (k, v) for k, v in sorted(kwargs.items()))),
        )

    def limit_for(self, expiration=10, **kwargs):
        """Set the rate limited key for the user and expire at least
        the given :param:`expiration` in seconds.

        :param expiration: A number of seconds to rate limited for.
        :param kwargs: Payload to identify this rate limit.
        """
        key = self._get_key(**kwargs)
        self.redis_conn.set(key, 1)
        self.redis_conn.expire(key, expiration)

    def is_limited(self, **kwargs):
        """Returns :type:`True` if the given :param:`kwargs` is rate limited.

        :param kwargs: Payload to identify this rate limit.
        """
        key = self._get_key(**kwargs)
        return self.redis_conn.exists(key)

    def time_left(self, **kwargs):
        """Returns the number of seconds left until the given payload
        is no longer rate limited.

        :param kwargs: Payload to identify this rate limit
        """
        key = self._get_key(**kwargs)
        return self.redis_conn.ttl(key)
