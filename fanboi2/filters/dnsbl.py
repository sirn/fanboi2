import socket
from ipaddress import ip_interface, ip_network

from . import register_filter


@register_filter(name='dnsbl')
class DNSBL(object):
    """Utility class for checking IP address against DNSBL providers."""

    def __init__(self, providers, services={}):
        if not providers:
            providers = tuple()
        self.providers = tuple(providers)

    def should_reject(self, payload):
        """Returns :type:`True` if the given IP address is listed in the
        DNSBL providers. Returns :type:`False` if not listed or no DNSBL
        providers present.

        :param payload: A filter payload.
        """
        for provider in self.providers:
            try:
                check = '.'.join(reversed(payload['ip_address'].split('.')))
                res = socket.gethostbyname("%s.%s." % (check, provider))
                ipaddr = ip_interface("%s/255.0.0.0" % (res,))
                if ipaddr.network == ip_network('127.0.0.0/8'):
                    return True
            except (socket.gaierror, ValueError):
                continue
        return False
