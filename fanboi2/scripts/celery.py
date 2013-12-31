import os
import sys
from fanboi2 import configure_components
from fanboi2.tasks import celery
from pyramid.paster import get_appsettings


def main(argv=sys.argv):
    if not len(argv) >= 2:
        sys.stderr.write("Usage: %s config\n" % os.path.basename(argv[0]))
        sys.stderr.write("Configuration file not present.\n")
        sys.exit(1)

    configure_components(get_appsettings(argv[1]))
    celery.start(argv[:1] + argv[2:])  # Remove argv[1].
