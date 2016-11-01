import hashlib
from .request import serialize_request
from ..models import redis_conn


class RateLimiter(object):
    """Rate limit to throttle content posting to every specific seconds."""

    def __init__(self, request, namespace=None):
        request = serialize_request(request)
        self.key = "rate:%s:%s" % (
            namespace,
            hashlib.md5(request['remote_addr'].encode('utf8')).hexdigest(),
        )

    def limit(self, seconds=10):
        """Mark user as rate limited for `seconds`.

        :param seconds: A number of seconds :type:`int` to rate limited for.

        :type seconds: int
        :rtype: None
        """
        redis_conn.set(self.key, 1)
        redis_conn.expire(self.key, seconds)

    def limited(self):
        """Returns true if content should be limited from posting.
        :rtype: bool
        """
        return redis_conn.exists(self.key)

    def timeleft(self):
        """Returns seconds left until user is no longer throttled.
        :rtype: int
        """
        return redis_conn.ttl(self.key)
