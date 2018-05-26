import datetime

from sqlalchemy.sql import desc, func, or_, and_

from ..models import RuleBan


class RuleBanCreateService(object):
    """Rule ban create service provides a service for creating ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(
        self, ip_address, description=None, duration=None, scope=None, active=True
    ):
        """Create a new rule ban.

        :param ip_address: An IP address or IP network to ban.
        :param description: Optional description.
        :param duration: Duration in days to auto-expire the ban.
        :param scope: Scope to apply the ban to (e.g. ``board:meta``)
        :param active: Boolean flag whether the ban should be active.
        """
        if not description:
            description = None

        active_until = None
        if duration:
            duration_delta = datetime.timedelta(days=duration)
            active_until = datetime.datetime.now() + duration_delta

        if not scope:
            scope = None

        rule_ban = RuleBan(
            ip_address=ip_address,
            description=description,
            scope=scope,
            active_until=active_until,
            active=bool(active),
        )

        self.dbsession.add(rule_ban)
        return rule_ban


class RuleBanQueryService(object):
    """Rule ban query service provides a service for query the ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_active(self):
        """Returns a list of bans that are currently active."""
        return list(
            self.dbsession.query(RuleBan)
            .filter(
                and_(
                    RuleBan.active == True,  # noqa: E712
                    or_(
                        RuleBan.active_until == None,  # noqa: E712
                        RuleBan.active_until >= func.now(),
                    ),
                )
            )
            .order_by(desc(RuleBan.active_until), desc(RuleBan.created_at))
            .all()
        )

    def list_inactive(self):
        """Returns a list of bans that are currently inactive."""
        return list(
            self.dbsession.query(RuleBan)
            .filter(
                or_(
                    RuleBan.active == False,  # noqa: E712
                    RuleBan.active_until <= func.now(),
                )
            )
            .order_by(desc(RuleBan.active_until), desc(RuleBan.created_at))
            .all()
        )

    def is_banned(self, ip_address, scopes=None):
        """Verify whether the IP address is in the ban list.

        :param ip_address: An IP address :type:`str` to lookup for.
        :param scopes: A scope :type:`str` to lookup for.
        """
        q = (
            self.dbsession.query(RuleBan)
            .filter(RuleBan.listed(ip_address, scopes))
            .exists()
        )
        return self.dbsession.query(q).scalar()

    def rule_ban_from_id(self, id_):
        """Retrieve a :class:`RuleBan` matching the given :param:`id`
        from the database or raise ``NoResultFound`` if not exists.

        :param id_: ID of the RuleBan to retrieve.
        """
        return self.dbsession.query(RuleBan).filter_by(id=id_).one()


class RuleBanUpdateService(object):
    """Rule ban create service provides a service for updating ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, id_, **kwargs):
        """Update the given rule ban ID with the given :param:`kwargs`.
        This method will raise ``NoResultFound`` if the given ID does not
        exists.

        :param id_: ID of the RuleBan to update.
        :param **kwargs: Attributes to update.
        """
        rule_ban = self.dbsession.query(RuleBan).filter_by(id=id_).one()

        if "duration" in kwargs and kwargs["duration"] != rule_ban.duration:
            active_until = None
            if kwargs["duration"]:
                duration_delta = datetime.timedelta(days=kwargs["duration"])
                active_until = rule_ban.created_at + duration_delta
            rule_ban.active_until = active_until

        if "active" in kwargs:
            rule_ban.active = bool(kwargs["active"])

        for key in ("ip_address", "description", "scope"):
            if key in kwargs:
                value = kwargs[key]
                if not value:
                    value = None
                setattr(rule_ban, key, value)

        self.dbsession.add(rule_ban)
        return rule_ban
