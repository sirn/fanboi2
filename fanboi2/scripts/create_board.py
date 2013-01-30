import optparse
import sys
import transaction
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config
from ..models import DBSession, Board


DESCRIPTION = "Insert a new board into the database."
USAGE = "Usage: %prog config arguments"


def main(config_uri=sys.argv[1], argv=sys.argv[2:]):
    parser = optparse.OptionParser(usage=USAGE, description=DESCRIPTION)
    parser.add_option('-t', '--title', dest='title', type='string')
    parser.add_option('-s', '--slug', dest='slug', type='string')

    options, args = parser.parse_args(argv)
    if options.title is None:
        parser.error('You must provide at least --title')

    slug = options.slug
    if slug is None:
        slug = options.title.lower().replace(' ', '_')

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        board = Board(title=options.title, slug=slug)
        DBSession.add(board)
        DBSession.flush()
        print("Successfully added %s (slug: %s)" % (board.title, board.slug))