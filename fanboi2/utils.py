import datetime
import hashlib
import requests
from pyramid.renderers import JSON
from sqlalchemy.orm import Query
from zope.interface.registry import Components
from zope.interface import Interface, providedBy
from .models import redis_conn, Base
from .version import __VERSION__


def serialize_request(request):
    """Serialize :class:`pyramid.util.Request` into a :type:`dict`."""

    if isinstance(request, dict):
        return request

    return {
        'application_url': request.application_url,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent,
        'referrer': request.referrer,
        'url': request.url,
    }


class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self):
        self.key = None

    def configure_key(self, key):
        self.key = key

    def _api_post(self, name, data=None):
        return requests.post(
            'https://%s.rest.akismet.com/1.1/%s' % (self.key, name),
            headers={'User-Agent': "Fanboi2/%s | Akismet/0.1" % __VERSION__},
            data=data)

    def spam(self, request, message):
        """Returns :type:`True` if `message` is spam. Always returns
        :type:`False` if Akismet key is not set.
        """
        if self.key:
            request = serialize_request(request)
            return self._api_post('comment-check', data={
                'blog': request['application_url'],
                'user_ip': request['remote_addr'],
                'user_agent': request['user_agent'],
                'referrer': request['referrer'],
                'permalink': request['url'],
                'comment_type': 'comment',
                'comment_content': message,
            }).content == b'true'
        return False


akismet = Akismet()


class RateLimiter(object):
    """Rate limit to throttle content posting to every specific seconds."""

    def __init__(self, request, namespace=None):
        request = serialize_request(request)
        self.key = "rate:%s:%s" % (
            namespace,
            hashlib.md5(request['remote_addr'].encode('utf8')).hexdigest(),
        )

    def limit(self, seconds=10):
        """Mark user as rate limited for `seconds`."""
        redis_conn.set(self.key, 1)
        redis_conn.expire(self.key, seconds)

    def limited(self):
        """Returns true if content should be limited from posting."""
        return redis_conn.exists(self.key)

    def timeleft(self):
        """Returns seconds left until user is no longer throttled."""
        return redis_conn.ttl(self.key)


json_renderer = JSON()


def _datetime_adapter(obj, request):
    """Serialize :type:`datetime.datetime` object into a string."""
    return obj.isoformat()


def _sqlalchemy_query_adapter(obj, request):
    """Serialize SQLAlchemy query into a list."""
    return [item for item in obj]


json_renderer.add_adapter(datetime.datetime, _datetime_adapter)
json_renderer.add_adapter(Query, _sqlalchemy_query_adapter)
