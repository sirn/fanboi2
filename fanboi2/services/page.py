from ..models import Page
from ..models.page import INTERNAL_PAGES


class PageCreateService(object):
    """Page create service provides a service for creating public page."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def create(self, slug, title, body):
        """Create a new public page.

        :param slug: The identifier of the page. Also used in URL.
        :param title: The title of the page.
        :param body: The content of the page.
        """
        page = Page(
            namespace='public',
            slug=slug,
            title=title,
            body=body,
            formatter='markdown')

        self.dbsession.add(page)
        return page

    def create_internal(self, slug, body, _internal_pages=INTERNAL_PAGES):
        """Create an internal page. Internal pages must be defined within
        the list of internal pages otherwise this method will raise
        :type:`ValueError`

        :param slug: The internal identifier of the page.
        :param body: The content of the internal page.
        """
        _pages = {p[0]: p[1] for p in _internal_pages}
        if slug not in _pages:
            raise ValueError(slug)

        page = Page(
            namespace='internal',
            slug=slug,
            title=slug,
            body=body,
            formatter=_pages[slug])

        self.dbsession.add(page)
        return page


class PageDeleteService(object):
    """Page create service provides a service for deleting page."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def delete(self, slug):
        """Delete a public page. This method will raise ``NoResultFound``
        if the given slug does not already exists.

        :param slug: An identifier of the page.
        """
        page = self.dbsession.query(Page).\
            filter_by(slug=slug, namespace='public').\
            one()

        self.dbsession.delete(page)
        return page

    def delete_internal(self, slug):
        """Delete an internal page. This method will raise ``NoResultFound``
        if the given slug does not already exists.

        :param slug: An identifier of the page.
        """
        page = self.dbsession.query(Page).\
            filter_by(slug=slug, namespace='internal').\
            one()

        self.dbsession.delete(page)
        return page


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

    def public_page_from_slug(self, slug):
        """Query a public page from the given page slug.

        :param page_slug: A slug :type:`str` identifying the page.
        """
        return self.dbsession.query(Page).\
            filter_by(namespace='public', slug=slug).\
            one()

    def internal_page_from_slug(self, slug, _internal_pages=INTERNAL_PAGES):
        """Query an internal page from the given page slug. This method will
        raise :type:`ValueError` if the given slug is not within the list of
        permitted pages.

        :param slug: A slug :type:`str` identifying the page.
        """
        _pages = {p[0]: p[1] for p in _internal_pages}
        if slug not in _pages:
            raise ValueError(slug)

        return self.dbsession.query(Page).\
            filter_by(namespace='internal', slug=slug).\
            one()


class PageUpdateService(object):
    """Page create service provides a service for updating page."""

    def __init__(self, dbsession):
        self.dbsession = dbsession

    def update(self, slug, **kwargs):
        """Update a public page matching the given :param:`slug`. This method
        will raise ``NoResultFound`` if the given slug does not already
        exists.

        :param slug: The page identifier.
        :param **kwargs: Attributes to update.
        """
        page = self.dbsession.query(Page).\
            filter_by(namespace='public', slug=slug).\
            one()

        for key in ('title', 'body'):
            if key in kwargs:
                setattr(page, key, kwargs[key])

        self.dbsession.add(page)
        return page

    def update_internal(self, slug, **kwargs):
        """Update an internal page matching the given :param:`slug`.
        This method will raise ``NoResultFound`` if the given slug does not
        already exists.

        :param slug: The page identifier.
        :param **kwargs: Attributes to update.
        """
        page = self.dbsession.query(Page).\
            filter_by(namespace='internal', slug=slug).\
            one()

        for key in ('body',):
            if key in kwargs:
                setattr(page, key, kwargs[key])

        self.dbsession.add(page)
        return page
