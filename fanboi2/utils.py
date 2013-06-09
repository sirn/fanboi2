import requests


class Akismet(object):
    """Basic integration between Pyramid and Akismet."""

    def __init__(self, request):
        self.request = request
        self.key = request.registry.settings.get('akismet.key')

    def _api_post(self, name, **kwargs):
        return requests.post(
            'https://%s.rest.akismet.com/1.1/%s' % (self.key, name),
            **kwargs)

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
