from ..models import Page
from ..models.page import INTERNAL_PAGES


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

    def list_internal(self, _internal_pages=INTERNAL_PAGES):
        """Query all internal pages. This method may return an unpersisted
        page object in case the internal page has been defined but has not
        been created.
        """
        db_pages = self.dbsession.query(Page).\
            filter_by(namespace='internal').\
            all()
        seen_slug = []
        pages = []
        for page in db_pages:
            pages.append(page)
            seen_slug.append(page.slug)
        for slug, formatter in _internal_pages:
            if slug not in seen_slug:
                pages.append(Page(
                    slug=slug,
                    formatter=formatter,
                    namespace='internal'))
        return sorted(pages, key=lambda p: p.slug)

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
