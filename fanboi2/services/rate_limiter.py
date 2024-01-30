import math


class RateLimiterService(object):
    """Rate limiter service provides a service for querying whether
    the user given by a payload should be rate-limited.
    """

    SCALED_LIMIT_PRUNE_PERIOD = 7200

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def _get_key(self, **kwargs):
        return "services.rate_limiter:%s" % (
            (",".join("%s=%s" % (k, v) for k, v in sorted(kwargs.items()))),
        )

    def limit_for(self, expiration=10, threshold=0, period=0, **kwargs):
        """Sets the rate limit depending on :param:`threshold` and :param:`period`.

        If zero, a naive limit algorithm will be used, which will use a static
        rate limit as set via :param:`expiration`.

        If non-zero, scaled limit algorithm will be used, which will scale
        rate limit from :param:`expiration` up in logarithmic series that will
        allow maximum of :param:`threshold` attempts within :param:`period`.

        Limits are tracked for up to 7,200 seconds. In other words, :param:`period`
        must not exceed `3600` (due to penalty calculation).

        :param expiration: A number of seconds to rate limited for.
        :param threshold: A maximum attempt per :param:`period`.
        :param period: A number of seconds to allow :param:`threshold: for.
        :param kwargs: Payload to identify this rate limit.
        """
        if not threshold or not period:
            return self._naive_limit_for(expiration, **kwargs)
        return self._scaled_limit_for(expiration, threshold, period, **kwargs)

    def _naive_limit_for(self, expiration, **kwargs):
        key = self._get_key(**kwargs)
        self.redis_conn.set(key, 1)
        self.redis_conn.expire(key, expiration)

    def _scaled_limit_for(self, expiration, threshold, period, **kwargs):
        redis_time = self.redis_conn.time()  # Avoid relying on local clock.
        ts = redis_time[0]
        ts_key = self._get_key(**{**kwargs, "type": "ts"})

        # We're using LRANGE instead of ZCOUNT/ZREMRANGEBYSCORE due to the lack
        # of Z commands support in our mock client (shhh...). This is subjected
        # to a race condition, but it's ok.
        self.redis_conn.rpush(ts_key, ts)
        all_ts = self.redis_conn.lrange(ts_key, 0, -1)
        prune_cutoff = ts - self.SCALED_LIMIT_PRUNE_PERIOD
        count = 0
        for t in all_ts:
            t = int(t)
            if t < prune_cutoff:
                self.redis_conn.lrem(ts_key, 0, t)
            else:
                count += 1
        self.redis_conn.expire(ts_key, self.SCALED_LIMIT_PRUNE_PERIOD)
        count = min(count, threshold)

        r = math.exp(math.log(period / 10) / (threshold - 1))
        t = round(expiration * (r ** (count - 1)))
        key = self._get_key(**kwargs)
        self.redis_conn.set(key, 1)
        self.redis_conn.expire(key, t)

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
