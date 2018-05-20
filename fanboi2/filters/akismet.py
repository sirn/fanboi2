import requests

from ..version import __VERSION__
from . import register_filter


@register_filter(name='akismet')
class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self, key, services={}):
        self.key = key

    def _api_post(self, name, data=None):
        """Make a request to Akismet API and return the response.

        :param name: A :type:`str` of API method name to request.
        :param data: A :type:`dict` payload.
        """
        return requests.post(
            'https://%s.rest.akismet.com/1.1/%s' % (self.key, name),
            headers={'User-Agent': "fanboi2/%s" % __VERSION__},
            data=data,
            timeout=2)

    def should_reject(self, payload):
        """Returns :type:`True` if the message is spam. Returns :type:`False`
        if the message was not a spam or Akismet was not configured.

        :param payload: A filter payload.
        """
        if self.key:
            try:
                return self._api_post('comment-check', data={
                    'comment_content': payload['body'],
                    'blog': payload['application_url'],
                    'user_ip': payload['ip_address'],
                    'user_agent': payload['user_agent'],
                    'referrer': payload['referrer'],
                }).content == b'true'
            except (KeyError, requests.Timeout):
                pass
        return False
