import re

from sqlalchemy.sql import desc, and_

from ..models import Banword


class BanwordCreateService(object):
    """Banword create service provides a service for creating banword."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(self, expr, description=None, scope=None, active=True):
        """Create a new banword.

        :param expr: A regular expression for the keyword to ban.
        :param description: A description for the banword.
        :param scope: A scope for the banword.
        :param active: Boolean flag whether the banword should be active.
        """
        if not expr:
            expr = None

        if not scope:
            scope = None

        if not description:
            description = None

        banword = Banword(
            expr=expr, description=description, scope=scope, active=bool(active)
        )
        self.dbsession.add(banword)
        return banword


class BanwordQueryService(object):
    """Banword query service provides a service for querying banwords."""

    def __init__(self, dbsession, scope_svc):
        self.dbsession = dbsession
        self.scope_svc = scope_svc

    def list_active(self):
        """Returns a list of banwords that are currently active."""
        return list(
            self.dbsession.query(Banword)
            .filter(and_(Banword.active == True))  # noqa: E712
            .order_by(desc(Banword.id))
        )

    def list_inactive(self):
        """Returns a list of banwords that are currently inactive."""
        return list(
            self.dbsession.query(Banword)
            .filter(and_(Banword.active == False))  # noqa: E712
            .order_by(desc(Banword.id))
        )

    def is_banned(self, text):
        """Verify whether the given text includes any of the banwords.

        :param text: A text to check.
        """
        for banword in self.list_active():
            banword_re = re.compile(banword.expr)
            if banword_re.search(text):
                return True
        return False

    def banword_from_id(self, id_):
        """Retrieve a :class:`Banword` matching the given :param:`id`
        from the database or raise ``NoResultFound`` if not exists.

        :param id_: ID of the banword to retrieve.
        """
        return self.dbsession.query(Banword).filter_by(id=id_).one()


class BanwordUpdateService(object):
    """Banword update service provides a service for updating banwords."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, banword_id, **kwargs):
        banword = self.dbsession.query(Banword).filter_by(id=banword_id).one()

        if "active" in kwargs:
            banword.active = bool(kwargs["active"])

        for key in ("expr", "description", "scope"):
            if key in kwargs:
                value = kwargs[key]
                if not value:
                    value = None
                setattr(banword, key, value)

        self.dbsession.add(banword)
        return banword
