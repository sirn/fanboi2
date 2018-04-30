import requests

from ..version import __VERSION__
from . import register_filter


class BlackBoxProxyDetector(object):
    """Provides integration with Black Block Proxy Block service."""

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        if not self.url:
            self.url = 'http://proxy.mind-media.com/block/proxycheck.php'

    def check(self, ip_address):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is not
        an error code returned from Black Box Proxy Block.

        :param ip_address: An :type:`str` IP address.
        """
        try:
            result = requests.get(
                self.url,
                headers={'User-Agent': "fanboi2/%s" % __VERSION__},
                params={'ip': ip_address},
                timeout=2)
        except requests.Timeout:
            return
        if result.status_code == 200 and result.content != b'X':
            return result.content

    def evaluate(self, result):
        """Evaluate result returned from the evaluation request. Return
        :type:`True` if evaluation result is 'Y', i.e. a proxy.

        :param result: A result from evaluation request.
        """
        if result == b'Y':
            return True
        return False


class GetIPIntelProxyDetector(object):
    """Provides integration with GetIPIntel proxy detection service."""

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        self.flags = kwargs.get('flags')
        self.email = kwargs.get('email')
        if not self.url:
            self.url = 'http://check.getipintel.net/check.php'
        if not self.email:
            raise ValueError('GetIPIntel require an email to be present.')

    def check(self, ip_address):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is
        positive.

        :param ip_address: An :type:`str` IP address.
        """
        params = {'contact': self.email, 'ip': ip_address}
        if self.flags:
            params['flags'] = self.flags
        try:
            result = requests.get(
                self.url,
                headers={'User-Agent': "fanboi2/%s" % __VERSION__},
                params=params,
                timeout=5)
        except requests.Timeout:
            return
        if result.status_code == 200 and float(result.content) >= 0:
            return result.content

    def evaluate(self, result):
        """Evaluate result returned from the evaluation request. Return
        :type:`True` if evaluation result is likely to be a proxy, with
        probability higher than ``0.99`` (for example, ``0.994120``).

        :param result: A result from evaluation request.
        """
        if float(result) > 0.99:
            return True
        return False


DETECTOR_PROVIDERS = {
    'blackbox': BlackBoxProxyDetector,
    'getipintel': GetIPIntelProxyDetector,
}


@register_filter(name='proxy')
class ProxyDetector(object):
    """Base class for dispatching proxy detection into multiple providers."""

    __use_services__ = ('cache',)
    __default_settings__ = {
        'blackbox': {
            'enabled': False,
            'url': 'http://proxy.mind-media.com/block/proxycheck.php',
        },
        'getipintel': {
            'enabled': False,
            'url':  'http://check.getipintel.net/check.php',
            'email': None,
            'flags': None,
        },
    }

    def __init__(self, settings=None, services={}):
        if not settings:
            settings = {}
        self.settings = settings
        self.cache_region = services['cache']

    def _get_cache_key(self, provider, ip_address):
        return 'filters.proxy:provider=%s,ip_address=%s' % (
            provider,
            ip_address)

    def should_reject(self, payload):
        """Returns :type:`True` if the given IP address is identified as
        proxy by one of the providers. Returns :type:`False` if the IP
        address was not identified as a proxy or no providers configured.

        :param payload: A filter payload.
        """
        for provider, settings in self.settings.items():
            if settings['enabled']:
                detector = DETECTOR_PROVIDERS[provider](**settings)
                result = self.cache_region.get_or_create(
                    self._get_cache_key(provider, payload['ip_address']),
                    lambda: detector.check(payload['ip_address']),
                    should_cache_fn=lambda v: v is not None,
                    expiration_time=21600)
                if result is not None and detector.evaluate(result):
                    return True
        return False
