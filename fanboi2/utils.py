import datetime
import hashlib
import requests
import socket
from IPy import IP
from pyramid.renderers import JSON
from sqlalchemy.orm import Query
from .models import redis_conn
from .version import __VERSION__


def serialize_request(request):
    """Serialize :class:`pyramid.request.Request` into a :type:`dict`.

    :param request: A :class:`pyramid.request.Request` object to serialize.

    :type request: pyramid.response.Request or dict
    :rtype: dict
    """

    if isinstance(request, dict):
        return request

    return {
        'application_url': request.application_url,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent,
        'referrer': request.referrer,
        'url': request.url,
    }


class Dnsbl(object) :
    """Utility class for checking IP address against DNSBL providers."""

    def __init__(self):
        self.providers = []

    def configure_providers(self, providers):
        if isinstance(providers, str):
            providers = providers.split()
        self.providers = providers

    def listed(self, ip_address):
        """Returns :type:`True` if the given IP address is listed in the
        DNSBL providers. Returns :type:`False` if not listed or no DNSBL
        providers present.
        """
        if self.providers:
            for provider in self.providers:
                try:
                    check = '.'.join(reversed(ip_address.split('.')))
                    res = socket.gethostbyname("%s.%s." % (check, provider))
                    if IP(res).make_net('255.0.0.0') == IP('127.0.0.0/8'):
                        return True
                except (socket.gaierror, ValueError):
                    continue
        return False


dnsbl = Dnsbl()


class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self):
        self.key = None

    def configure_key(self, key):
        """Configure this :class:`Akismet` instance with the provided key.

        :param key: A :type:`str` Akismet API key.

        :type key: str
        :rtype: None
        """
        self.key = key

    def _api_post(self, name, data=None):
        """Make a request to Akismet API and return the response.

        :param name: A :type:`str` of API method name to request.
        :param data: A :type:`dict` payload.

        :type name: str
        :type data: dict
        :rtype: requests.models.Response
        """
        return requests.post(
            'https://%s.rest.akismet.com/1.1/%s' % (self.key, name),
            headers={'User-Agent': "Fanboi2/%s | Akismet/0.1" % __VERSION__},
            data=data,
            timeout=2)

    def spam(self, request, message):
        """Returns :type:`True` if `message` is spam. Always returns
        :type:`False` if Akismet key is not set or the request to Akismet
        was timed out.

        :param request: A :class:`pyramid.request.Request` object.
        :param message: A :type:`str` to identify.

        :type request: pyramid.request.Request or dict
        :type message: str
        :rtype: bool
        """
        if self.key:
            request = serialize_request(request)
            try:
                return self._api_post('comment-check', data={
                    'blog': request['application_url'],
                    'user_ip': request['remote_addr'],
                    'user_agent': request['user_agent'],
                    'referrer': request['referrer'],
                    'permalink': request['url'],
                    'comment_type': 'comment',
                    'comment_content': message,
                }).content == b'true'
            except requests.Timeout:
                return False
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


json_renderer = JSON()


def _datetime_adapter(obj, request):
    """Serialize :type:`datetime.datetime` object into a string.

    :param obj: A :class:`datetime.datetime` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: datetime.datetime
    :type request: pyramid.request.Request
    """
    return obj.isoformat()


def _sqlalchemy_query_adapter(obj, request):
    """Serialize SQLAlchemy query into a list.

    :param obj: An iterable SQLAlchemy's :class:`sqlalchemy.orm.Query` object.
    :param request: A :class:`pyramid.request.Request` object.

    :type obj: sqlalchemy.orm.Query
    :type request: pyramid.request.Request
    """
    return [item for item in obj]


json_renderer.add_adapter(datetime.datetime, _datetime_adapter)
json_renderer.add_adapter(Query, _sqlalchemy_query_adapter)
