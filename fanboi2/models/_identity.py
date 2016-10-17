import datetime
import hashlib
import pytz
import random
import string


class Identity(object):
    """Generates a unique user identity for each user based on IP address."""
    STRINGS = string.ascii_letters + string.digits + "+/."

    def __init__(self, redis=None):
        self.timezone = pytz.utc
        self.redis = redis

    def configure_tz(self, timezone):
        """Configure timezone to use for key generation.

        :param timezone: A timezone :type:`str`.

        :type timezone: str
        :rtype: None
        """
        self.timezone = pytz.timezone(timezone)

    def _key(self, ip_address, namespace="default"):
        """Generate a unique key for each :attr:`ip_address` under namespace
        :attr:`namespace`. Generated key will contain the current date in
        the configured timezone to ensure key is unique to each day.

        :param ip_address: An IP address :type:`str`.
        :param namespace: A namespace :type:`str` to generate key in.
        :type ip_address: str
        :type namespace: str
        :rtype: str
        """
        today = datetime.datetime.now(self.timezone).strftime("%Y%m%d")
        return "ident:%s:%s:%s" % (today,
                                   namespace,
                                   hashlib.md5(ip_address.encode('utf8')).
                                       hexdigest())

    def get(self, *args, **kwargs):
        """Retrieve user ident from Redis or generate a new one if it does
        not already exists. Ident is generated from a random string and
        expired every 24 hours.

        :param args: Arguments that will be passed to :meth:`_key`.
        :param kwargs: Keyword arguments that will be passed to :meth:`_key`.

        :type args: list
        :type kwargs: dict
        :rtype: str
        """
        key = self._key(*args, **kwargs)
        ident = self.redis.get(key)
        if ident is None:
            ident = ''.join(random.choice(self.STRINGS) for x in range(9))
            self.redis.setnx(key, ident)
            self.redis.expire(key, 86400)
        else:
            ident = ident.decode('utf-8')
        return ident
