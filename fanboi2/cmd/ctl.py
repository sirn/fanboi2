import argparse
import code
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
    import hupper
    from waitress import serve as waitress_serve
    from ..wsgi import app

    if args.reload:
        hupper.start_reloader("fanboi2.cmd.ctl.main")

    waitress_serve(app, host=args.host, port=args.port)
    sys.exit(0)


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

    pserve = subparsers.add_parser("serve")
    pserve.add_argument("--port", type=int, default=6543)
    pserve.add_argument("--host", default="0.0.0.0")
    pserve.add_argument("--reload", action="store_true")
    pserve.set_defaults(func=serve)

    gsecret = subparsers.add_parser("gensecret")
    gsecret.set_defaults(func=gensecret)

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_usage()
        sys.exit(1)

    args.func(args)
