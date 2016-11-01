import requests
from ..version import __VERSION__
from ..cache import cache_region as cache_region_


class BlackBoxProxyDetector(object):
    """Provides integration with Black Block Proxy Block service."""

    def __init__(self, config):
        self.url = config.get('url')
        if not self.url:
            self.url = 'http://www.shroomery.org/ythan/proxycheck.php'

    def check(self, ip_address):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is not
        an error code returned from Black Box Proxy Block.

        :param ip_address: An :type:`str` IP address.

        :type ip_address: str
        :rtype: str or None
        """
        try:
            result = requests.get(
                self.url,
                headers={'User-Agent': "Fanboi2/%s" % __VERSION__},
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

        :type result: str
        :rtype: bool
        """
        if result == b'Y':
            return True
        return False


class GetIPIntelProxyDetector(object):
    """Provides integration with GetIPIntel proxy detection service."""

    def __init__(self, config):
        self.url = config.get('url')
        self.flags = config.get('flags')
        self.email = config.get('email')
        if not self.url:
            self.url = 'http://check.getipintel.net/check.php'
        if not self.email:
            raise ValueError('GetIPIntel require an email to be present.')

    def check(self, ip_address):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is
        positive.

        :param ip_address: An :type:`str` IP address.

        :type ip_address: str
        :rtype: str or None
        """
        params = {'contact': self.email, 'ip': ip_address}
        if self.flags:
            params['flags'] = self.flags
        try:
            result = requests.get(
                self.url,
                headers={'User-Agent': "Fanboi2/%s" % __VERSION__},
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

        :type result: str
        :rtype: bool
        """
        if float(result) > 0.99:
            return True
        return False


DETECTOR_PROVIDERS = {
    'blackbox': BlackBoxProxyDetector,
    'getipintel': GetIPIntelProxyDetector,
}


class ProxyDetector(object):
    """Base class for dispatching proxy detection into multiple providers."""

    def __init__(self, cache_region=cache_region_):
        self.providers = []
        self.instances = {}
        self.cache_region = cache_region

    def configure_from_config(self, config, key=None):
        """Configure and initialize proxy detectors. The configuration dict
        may contains provider-specific configuration using the same dotted-
        name as the provider itself, for example ``getipintel.url``.

        If the configuration key is prefixed with other dotted names, ``key``
        may be given to extract from that prefix.

        :param config: Configuration :type:`dict`.
        :param key: Key prefix to extract configuration.
        """
        if key is None:
            key = ''
        self.providers = config.get('%sproviders' % (key,), [])
        for provider in self.providers:
            class_ = DETECTOR_PROVIDERS[provider]
            provider_key = "%s%s." % (key, provider)
            provider_config = {}
            for k, v in config.items():
                if k.startswith(provider_key):
                    provider_config[k[len(provider_key):]] = v
            self.instances[provider] = class_(provider_config)

    def detect(self, ip_address):
        """Detect if the given ``ip_address`` is a proxy using providers
        configured via :meth:``configure_from_config``.

        :param ip_address: An IP address to perform a proxy check against.
        :type ip_address: str
        :rtype: bool
        """
        for provider in self.providers:
            detector = self.instances[provider]
            result = self.cache_region.get_or_create(
                'proxy:%s:%s' % (provider, ip_address),
                lambda: detector.check(ip_address),
                should_cache_fn=lambda v: v is not None,
                expiration_time=21600)
            if result is not None and detector.evaluate(result):
                return True
        return False
