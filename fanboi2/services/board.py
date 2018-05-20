from ..models import Board


class BoardCreateService(object):
    """Board create service provides a service for creating board."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(self, slug, title, description, status, agreements, settings):
        """Create a new board.

        :param slug: An identifier of the board. Also used in URL.
        :param title: Name of the board.
        :param description: Descripton explaining what the board is about.
        :param status: Status of the board.
        :param agreements: Term of use for the board.
        :param settings: Settings for the board.
        """
        board = Board(
            slug=slug,
            title=title,
            description=description,
            status=status,
            agreements=agreements,
            settings=settings)

        self.dbsession.add(board)
        return board


class BoardQueryService(object):
    """Board query service provides a service for querying a board
    or a collection of boards from the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_all(self):
        """Query all boards."""
        return list(
            self.dbsession.query(Board).
            order_by(Board.title).
            all())

    def list_active(self):
        """Query all boards that are not archived."""
        return list(
            self.dbsession.query(Board).
            order_by(Board.title).
            filter(Board.status != 'archived').
            all())

    def board_from_slug(self, board_slug):
        """Query a board from the given board slug.

        :param board_slug: The slug :type:`str` identifying a board.
        """
        return self.dbsession.query(Board).\
            filter_by(slug=board_slug).\
            one()


class BoardUpdateService(object):
    """Board update service provides a service for updating board."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, slug, **kwargs):
        """Update the given board slug with the given :param:`kwargs`.
        This method will raise ``NoResultFound`` if the given slug does not
        already exists. Slug cannot be updated.

        :param slug: The board identifier.
        :param **kwargs: Attributes to update.
        """
        board = self.dbsession.query(Board).filter_by(slug=slug).one()

        for key in (
                'title',
                'description',
                'status',
                'agreements',
                'settings'):
            if key in kwargs:
                setattr(board, key, kwargs[key])

        self.dbsession.add(board)
        return board
