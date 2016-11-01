import requests
from .request import serialize_request
from ..version import __VERSION__


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
            headers={'User-Agent': "Fanboi2/%s" % __VERSION__},
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
