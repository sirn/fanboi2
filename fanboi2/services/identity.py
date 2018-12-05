import string
import random


STRINGS = string.ascii_letters + string.digits + "+/."


class IdentityService(object):
    """Identity service provides a service for querying an identity
    for a user given by a payload from the database or generate a new
    one if not already exists.
    """

    def __init__(self, redis_conn, setting_query_svc):
        self.redis_conn = redis_conn
        self.ident_size = setting_query_svc.value_from_key("app.ident_size")

    def _get_key(self, **kwargs):
        return "services.identity:%s" % (
            (",".join("%s=%s" % (k, v) for k, v in sorted(kwargs.items()))),
        )

    def identity_for(self, **kwargs):
        """Query the identity for user matching :param:`kwargs` payload
        or generate a new one if not exists.

        :param payload: Payload to identify this rate limit.
        """
        key = self._get_key(**kwargs)
        ident = self.redis_conn.get(key)

        if ident is not None:
            return ident.decode("utf-8")

        ident = "".join(random.choice(STRINGS) for x in range(self.ident_size))
        self.redis_conn.setnx(key, ident)
        self.redis_conn.expire(key, 86400)
        return ident
