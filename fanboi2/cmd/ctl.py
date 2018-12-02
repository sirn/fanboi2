import argparse
import code
import multiprocessing
import sys

from ..version import __VERSION__, __PYRAMID__


SHELL_BANNER = """\
      ___  ___
    / /     / /
   /_/_   _/_/    fanboi2 %s
  / /   / /       pyramid %s
 /_/   /_/__

Loaded locals:

    app           Fanboi2 WSGI application
    config        Pyramid configurator
    registry      Pyramid registry
    request       Pyramid request context
    root          Pyramid root
    root_factory  Pyramid root factory
"""


def shell(args):
    """Run the interactive shell for the application."""
    from ..wsgi import app, config
    import pyramid.scripting

    with pyramid.scripting.prepare() as env:
        code.interact(
            SHELL_BANNER % (__VERSION__, __PYRAMID__),
            local={"app": app, "config": config, **env},
        )


def serve(args):
    """Run the web server for the application."""
    from gunicorn.app.base import BaseApplication
    from ..wsgi import app as wsgi_app

    class FbserveApplication(BaseApplication):
        def __init__(self, app, options=None):
            if not options:
                options = {}
            self.options = options
            self.application = app
            super(FbserveApplication, self).__init__()

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": "%s:%s" % (args.host, args.port),
        "max_requests": args.max_requests,
        "reload": args.reload,
        "threads": args.threads,
        "workers": args.workers,
    }

    FbserveApplication(wsgi_app, options).run()


def gensecret(args):
    """Generates a NaCl secret."""
    from pyramid_nacl_session import generate_secret

    print(generate_secret(as_hex=True).decode("utf-8"))
    sys.exit(0)


def main():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", title="subcommands")

    pshell = subparsers.add_parser("shell")
    pshell.set_defaults(func=shell)

    cpu_count = multiprocessing.cpu_count()
    pserve = subparsers.add_parser("serve")
    pserve.add_argument("--port", type=int, default=6543)
    pserve.add_argument("--host", default="0.0.0.0")
    pserve.add_argument("--workers", type=int, default=(cpu_count * 2) + 1)
    pserve.add_argument("--threads", type=int, default=1)
    pserve.add_argument("--max-requests", type=int, default=1000)
    pserve.add_argument("--reload", action="store_true")
    pserve.set_defaults(func=serve)

    gsecret = subparsers.add_parser("gensecret")
    gsecret.set_defaults(func=gensecret)

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_usage()
        sys.exit(1)

    args.func(args)
