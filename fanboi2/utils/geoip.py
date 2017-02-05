import logging
import geoip2.database
from maxminddb.errors import InvalidDatabaseError
from geoip2.errors import AddressNotFoundError


log = logging.getLogger(__name__)


class GeoIP(object):
    """Utility for looking up IP address against GeoIP database."""

    def __init__(self):
        self.geoip2 = None

    def configure_geoip2(self, path):
        """Configure and initialize GeoIP2 database with the given ``path``
        and warn if GeoIP2 database could not be loaded. If no GeoIP2 database
        could be initialized, all of its operations will return :type:`None`.

        :param path: Path to the GeoIP2 database file (mmdb).
        :type path: str
        """
        if path is not None:
            try:
                self.geoip2 = geoip2.database.Reader(path)
            except (FileNotFoundError, InvalidDatabaseError):
                pass
        if self.geoip2 is not None:
            return
        log.warn(
            'GeoIP2 database does not exists or invalid. ' +
            'Functionalities relying on GeoIP will not work.')

    def country_code(self, ip_address):
        """Resolve the given ``ip_address`` to 2-letter country code.

        :param ip_address: IP address to lookup.
        :type ip_address: str
        """
        response = None
        if self.geoip2 is not None:
            try:
                response = self.geoip2.country(ip_address)
            except AddressNotFoundError:
                pass
        if response is not None:
            return response.country.iso_code
