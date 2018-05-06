from sqlalchemy.sql import desc, func, or_, and_

from ..models import RuleBan


class RuleBanQueryService(object):
    """Rule ban query service provides a service for query the ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_active(self):
        """Returns a list of bans that are currently active."""
        return list(
            self.dbsession.query(RuleBan).
            filter(
                and_(RuleBan.active == True,  # noqa: E712
                     or_(RuleBan.active_until == None,  # noqa: E712
                         RuleBan.active_until >= func.now()))).
            order_by(desc(RuleBan.active_until),
                     desc(RuleBan.created_at)).
            all())

    def list_inactive(self):
        """Returns a list of bans that are currently inactive."""
        return list(
            self.dbsession.query(RuleBan).
            filter(
                or_(RuleBan.active == False,  # noqa: E712
                    RuleBan.active_until <= func.now())).
            order_by(desc(RuleBan.active_until),
                     desc(RuleBan.created_at)).
            all())

    def is_banned(self, ip_address, scopes=None):
        """Verify whether the IP address is in the ban list.

        :param ip_address: An IP address :type:`str` to lookup for.
        :param scopes: A scope :type:`str` to lookup for.
        """
        q = self.dbsession.query(RuleBan).\
            filter(RuleBan.listed(ip_address, scopes)).\
            exists()
        return self.dbsession.query(q).scalar()
