import socket
from ipaddress import ip_interface, ip_network


class Dnsbl(object):
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
                    ipaddr = ip_interface("%s/255.0.0.0" % (res,))
                    if ipaddr.network == ip_network('127.0.0.0/8'):
                        return True
                except (socket.gaierror, ValueError):
                    continue
        return False
