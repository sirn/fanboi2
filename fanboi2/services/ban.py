import datetime
import ipaddress

from sqlalchemy.sql import desc, func, or_, and_

from ..models import Ban


class BanCreateService(object):
    """Ban create service provides a service for creating ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(
        self, ip_address, description=None, duration=None, scope=None, active=True
    ):
        """Create a new ban.

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
            active_until = func.now() + duration_delta

        if not scope:
            scope = None

        ban = Ban(
            ip_address=ip_address,
            description=description,
            scope=scope,
            active_until=active_until,
            active=bool(active),
        )

        self.dbsession.add(ban)
        return ban


class BanQueryService(object):
    """Ban query service provides a service for query the ban list."""

    def __init__(self, dbsession, scope_svc):
        self.dbsession = dbsession
        self.scope_svc = scope_svc

    def list_active(self):
        """Returns a list of bans that are currently active."""
        return list(
            self.dbsession.query(Ban)
            .filter(
                and_(
                    Ban.active == True,  # noqa: E712
                    or_(
                        Ban.active_until == None,  # noqa: E712
                        Ban.active_until >= func.now(),
                    ),
                )
            )
            .order_by(desc(Ban.active_until), desc(Ban.created_at))
            .all()
        )

    def list_inactive(self):
        """Returns a list of bans that are currently inactive."""
        return list(
            self.dbsession.query(Ban)
            .filter(
                or_(Ban.active == False, Ban.active_until <= func.now())  # noqa: E712
            )
            .order_by(desc(Ban.active_until), desc(Ban.created_at))
            .all()
        )

    def is_banned(self, ip_address, scopes=None):
        """Verify whether the IP address is in the ban list.

        :param ip_address: An IP address :type:`str` to lookup for.
        :param scopes: A scope :type:`dict` for evaluating ban scope.
        """
        if not scopes:
            scopes = {}
        local_addr = ipaddress.ip_address(ip_address)
        for ban in self.list_active():
            if not ban.scope or self.scope_svc.evaluate(ban.scope, scopes):
                if local_addr in ipaddress.ip_network(ban.ip_address):
                    return ban

    def ban_from_id(self, id_):
        """Retrieve a :class:`Ban` matching the given :param:`id`
        from the database or raise ``NoResultFound`` if not exists.

        :param id_: ID of the Ban to retrieve.
        """
        return self.dbsession.query(Ban).filter_by(id=id_).one()


class BanUpdateService(object):
    """Ban update service provides a service for updating ban list."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, id_, **kwargs):
        """Update the given ban ID with the given :param:`kwargs`.
        This method will raise ``NoResultFound`` if the given ID does not
        exists.

        :param id_: ID of the Ban to update.
        :param **kwargs: Attributes to update.
        """
        ban = self.dbsession.query(Ban).filter_by(id=id_).one()

        if "duration" in kwargs and kwargs["duration"] != ban.duration:
            active_until = None
            if kwargs["duration"]:
                duration_delta = datetime.timedelta(days=kwargs["duration"])
                active_until = ban.created_at + duration_delta
            ban.active_until = active_until

        if "active" in kwargs:
            ban.active = bool(kwargs["active"])

        for key in ("ip_address", "description", "scope"):
            if key in kwargs:
                value = kwargs[key]
                if not value:
                    value = None
                setattr(ban, key, value)

        self.dbsession.add(ban)
        return ban
