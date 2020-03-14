import math
import requests
from ipaddress import ip_address

from ..version import __VERSION__
from . import register_filter


class BlackBoxProxyDetector(object):
    """Provides integration with Black Block Proxy Block service."""

    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        if not self.url:
            self.url = "http://proxy.mind-media.com/block/proxycheck.php"

    def can_check(self, ipaddr):
        """Returns :type:`True` if this detector can check the given
        IP address.

        :param ipaddr: An :type:`str` IP address.
        """
        return ip_address(ipaddr).version == 4

    def check(self, ipaddr):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is not
        an error code returned from Black Box Proxy Block.

        :param ipaddr: An :type:`str` IP address.
        """
        try:
            result = requests.get(
                self.url,
                headers={"User-Agent": "fanboi2/%s" % __VERSION__},
                params={"ip": ipaddr},
                timeout=2,
            )
        except requests.Timeout:
            return
        if result.status_code == 200 and result.content != b"X":
            return result.content

    def evaluate(self, result):
        """Evaluate result returned from the evaluation request. Return
        :type:`True` if evaluation result is 'Y', i.e. a proxy.

        :param result: A result from evaluation request.
        """
        if result == b"Y":
            return True
        return False


class GetIPIntelProxyDetector(object):
    """Provides integration with GetIPIntel proxy detection service."""

    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.flags = kwargs.get("flags")
        self.email = kwargs.get("email")
        self.threshold = kwargs.get("threshold")
        if not self.url:
            self.url = "http://check.getipintel.net/check.php"
        if not self.email:
            raise ValueError("GetIPIntel require an email to be present.")

    def can_check(self, ipaddr):
        """Returns :type:`True` if this detector can check the given
        IP address.

        :param ipaddr: An :type:`str` IP address.
        """
        return ip_address(ipaddr).version == 4

    def check(self, ipaddr):
        """Request for IP evaluation and return raw results. Return the
        response as-is if return code is 200 and evaluation result is
        positive.

        :param ipaddr: An :type:`str` IP address.
        """
        params = {"contact": self.email, "ip": ipaddr}
        if self.flags:
            params["flags"] = self.flags
        try:
            result = requests.get(
                self.url,
                headers={"User-Agent": "fanboi2/%s" % __VERSION__},
                params=params,
                timeout=5,
            )
        except requests.Timeout:
            return
        if result.status_code == 200 and float(result.content) >= 0:
            return result.content

    def evaluate(self, result):
        """Evaluate result returned from the evaluation request. Return
        :type:`True` if evaluation result is likely to be a proxy, with
        probability higher than a given threshold (default ``0.99``).

        :param result: A result from evaluation request.
        """
        try:
            threshold = float(self.threshold)
        except (ValueError, TypeError):
            threshold = None
        if not threshold or math.isnan(threshold):
            threshold = 0.99
        if float(result) > float(threshold):
            return True
        return False


DETECTOR_PROVIDERS = {
    "blackbox": BlackBoxProxyDetector,
    "getipintel": GetIPIntelProxyDetector,
}


@register_filter(name="proxy")
class ProxyDetector(object):
    """Base class for dispatching proxy detection into multiple providers."""

    __use_services__ = ("cache",)

    def __init__(self, settings=None, services=None):
        if not settings:
            settings = {}
        if not services:
            raise RuntimeError("cache service is required")
        self.settings = settings
        self.cache_region = services["cache"]

    def _get_cache_key(self, provider, ipaddr):
        return "filters.proxy:provider=%s,ip_address=%s" % (provider, ipaddr)

    def should_reject(self, payload):
        """Returns :type:`True` if the given IP address is identified as
        proxy by one of the providers. Returns :type:`False` if the IP
        address was not identified as a proxy or no providers configured.

        :param payload: A filter payload.
        """
        for provider, settings in self.settings.items():
            if settings["enabled"]:
                detector = DETECTOR_PROVIDERS[provider](**settings)
                ipaddr = payload["ip_address"]
                if not detector.can_check(ipaddr):
                    return False
                result = self.cache_region.get_or_create(
                    self._get_cache_key(provider, ipaddr),
                    lambda: detector.check(ipaddr),
                    should_cache_fn=lambda v: v is not None,
                    expiration_time=21600,
                )
                if result is not None and detector.evaluate(result):
                    return True
        return False
