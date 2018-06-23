import re

from sqlalchemy.sql import desc, and_

from ..models import Banword


class IBanwordCreateService(object):
    """Banword create service provides a service for creating banword."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(self, expression, active=True):
        """Create a new banword.

        :param expression: A regular expression for the keyword to ban.
        :param active: Boolean flag whether the banword should be active.
        """
        banword = Banword(expression=expression, active=bool(active))
        self.dbsession.add(banword)
        return banword


class IBanwordQueryService(object):
    """Banword query service provides a service for querying banwords."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

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
            banword_re = re.compile(banword.expression)
            if banword_re.search(text):
                return True
        return False

    def banword_from_id(self, id_):
        """Retrieve a :class:`Banword` matching the given :param:`id`
        from the database or raise ``NoResultFound`` if not exists.

        :param id_: ID of the banword to retrieve.
        """
        return self.dbsession.query(Banword).filter_by(id=id_).one()


class IBanwordUpdateService(object):
    """Banword update service provides a service for updating banwords."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, banword_id, **kwargs):
        pass
