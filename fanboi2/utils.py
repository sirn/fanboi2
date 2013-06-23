import hashlib
import requests
from . import __VERSION__


class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self, request):
        self.request = request
        self.key = request.registry.settings.get('akismet.key')

    def _api_post(self, name, data=None):
        return requests.post(
            'https://%s.rest.akismet.com/1.1/%s' % (self.key, name),
            headers={'User-Agent': "Fanboi2/%s | Akismet/0.1" % __VERSION__},
            data=data)

    def spam(self, message):
        """Returns :type:`True` if `message` is spam. Always returns
        :type:`False` if Akismet key is not set.
        """
        if self.key:
            return self._api_post('comment-check', data={
                'blog': self.request.application_url,
                'user_ip': self.request.remote_addr,
                'user_agent': self.request.user_agent,
                'referrer': self.request.referrer,
                'permalink': self.request.url,
                'comment_type': 'comment',
                'comment_content': message,
            }).content == b'true'
        return False


class RateLimiter(object):
    """Rate limit to throttle content posting to every specific seconds."""

    def __init__(self, request, namespace=None):
        self.request = request
        self.key = "rate:%s:%s" % (
            namespace,
            hashlib.md5(request.remote_addr.encode('utf8')).hexdigest(),
        )

    def limit(self, seconds=10):
        """Mark user as rate limited for `seconds`."""
        self.request.redis.set(self.key, 1)
        self.request.redis.expire(self.key, seconds)

    def limited(self):
        """Returns true if content should be limited from posting."""
        return self.request.redis.exists(self.key)

    def timeleft(self):
        """Returns seconds left until user is no longer throttled."""
        return self.request.redis.ttl(self.key)
