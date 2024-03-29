import argparse
import code
import sys

from ..version import __PYRAMID__, __VERSION__

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


def run_shell(args):
    """Run the interactive shell for the application."""
    import pyramid.scripting

    from .. import make_configurator
    from ..settings import settings_from_env

    settings = settings_from_env()
    config = make_configurator(settings)
    app = config.make_wsgi_app()
    with pyramid.scripting.prepare() as env:
        code.interact(
            SHELL_BANNER % (__VERSION__, __PYRAMID__),
            local={"app": app, "config": config, **env},
        )


def run_serve(args):
    """Run the web server for the application."""
    from waitress import serve as waitress_serve

    from .. import make_configurator, setup_logger
    from ..settings import settings_from_env

    if args.reload:
        try:
            import hupper
        except ImportError:
            sys.stderr.write("Please install dev dependencies to use reloader.\n")
            sys.exit(1)
        hupper.start_reloader("fanboi2.cmd.ctl.main")

    settings = settings_from_env()
    setup_logger(settings)
    config = make_configurator(settings)
    wsgi_app = config.make_wsgi_app()

    waitress_serve(wsgi_app, host=args.host, port=args.port, threads=args.threads)
    sys.exit(0)


def run_gensecret(args):
    """Generates a NaCl secret."""
    from pyramid_nacl_session import generate_secret

    print(generate_secret(as_hex=True).decode("utf-8"))
    sys.exit(0)


def main():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", title="subcommands")

    shell = subparsers.add_parser("shell")
    shell.set_defaults(func=run_shell)

    serve = subparsers.add_parser("serve")
    serve.add_argument("--port", type=int, default=6543)
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--threads", default=4)
    serve.add_argument("--reload", action="store_true")
    serve.set_defaults(func=run_serve)

    gensecret = subparsers.add_parser("gensecret")
    gensecret.set_defaults(func=run_gensecret)

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_usage()
        sys.exit(1)

    args.func(args)
