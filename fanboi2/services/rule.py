from ..models import RuleBan


class RuleBanQueryService(object):
    """Rule ban query service provides a service for query the ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def is_banned(self, ip_address, scopes=None):
        """Verify whether the IP address is in the ban list.

        :param ip_address: An IP address :type:`str` to lookup for.
        :param scopes: A scope :type:`str` to lookup for.
        """
        q = self.dbsession.query(RuleBan).\
            filter(RuleBan.listed(ip_address, scopes)).\
            exists()
        return self.dbsession.query(q).scalar()
