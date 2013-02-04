import json
import optparse
import os
import sys
import tempfile
import transaction
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound
from subprocess import call
from fanboi2 import DBSession
from fanboi2.models import Board, JsonType


DESCRIPTION = "Update board settings."
USAGE = "Usage: %prog config arguments"


def main(config_uri=sys.argv[1], argv=sys.argv[2:]):
    parser = optparse.OptionParser(usage=USAGE, description=DESCRIPTION)
    parser.add_option('-f', '--field', dest='field', type='string')
    parser.add_option('-s', '--slug', dest='slug', type='string')

    options, args = parser.parse_args(argv)
    if options.field is None:
        parser.error('You must provide --field')
    if options.slug is None:
        parser.error('You must provide --slug')

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        original = None
        modified = None
        board = None
        serialized = False

        try:
            board = DBSession.query(Board).filter_by(slug=options.slug).one()
        except NoResultFound:
            print('No board with %s slug found.' % options.slug)
            sys.exit(1)

        try:
            original = getattr(board, options.field)
        except AttributeError:
            print('No field %s found in board.' % options.field)
            sys.exit(1)

        with tempfile.NamedTemporaryFile(suffix='.tmp') as tmp:
            if original is not None:
                if isinstance(getattr(Board, options.field).type, JsonType):
                    serialized = True
                    dumps = json.dumps(original, indent=4)
                    tmp.write(bytes(dumps.encode('utf8')))
                else:
                    tmp.write(bytes(str(original).encode('utf8')))
                tmp.flush()
            call([os.environ.get('EDITOR', 'vi'), tmp.name])
            modified = open(tmp.name, "r").read()

        if serialized:
            modified = json.loads(modified)
        else:
            original = original if original is not None else str()
            modified = modified.rstrip("\r\n")

        if modified == original:
            print('Not modified.')
        else:
            setattr(board, options.field, modified)
            DBSession.add(board)
            print('Successfully updated %s for %s.' %
                  (options.field, board.title))
