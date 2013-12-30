import os
import sys
from pyramid.paster import bootstrap
from fanboi2.tasks import celery, configure_celery


def main(argv=sys.argv):
    if not len(argv) >= 2:
        sys.stderr.write("Usage: %s config\n" % os.path.basename(argv[0]))
        sys.stderr.write("Configuration file not present.\n")
        sys.exit(1)

    app = bootstrap(argv[1])
    celery_app = configure_celery(celery, app['registry'].settings)
    celery_app.start(argv[:1] + argv[2:])  # Remove argv[1].
