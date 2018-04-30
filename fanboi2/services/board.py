from ..models import Board


class BoardQueryService(object):
    """Board query service provides a service for querying a board
    or a collection of boards from the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_active(self):
        """Query all boards that are not archived."""
        return list(
            self.dbsession.query(Board).
            order_by(Board.title).
            filter(Board.status != 'archived'))

    def board_from_slug(self, board_slug):
        """Query a board from the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return self.dbsession.query(Board).\
            filter_by(slug=board_slug).\
            one()
