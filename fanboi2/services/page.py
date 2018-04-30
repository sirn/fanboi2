from ..models import Page


class PageQueryService(object):
    """Page query service provides a service for querying a page
    or a collection of pages from the database.
    """

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def list_public(self):
        """Query all public pages."""
        return list(
            self.dbsession.query(Page).
            order_by(Page.title).
            filter_by(namespace='public'))

    def public_page_from_slug(self, page_slug):
        """Query a public page from the given page slug.

        :param page_slug: A slug :type:`str` identifying the page.
        """
        return self.dbsession.query(Page).\
            filter_by(namespace='public', slug=page_slug).\
            one()

    def internal_page_from_slug(self, page_slug):
        """Query an internal page from the given page slug.

        :param page_slug: A slug :type:`str` identifying the page.
        """
        return self.dbsession.query(Page).\
            filter_by(namespace='internal', slug=page_slug).\
            one()
