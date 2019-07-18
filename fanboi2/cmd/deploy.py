import argparse
import datetime
import getpass
import os
import shlex
import sys
import uuid

try:
    from colorama import init, Fore, Style
    from fabric import Connection
    from invoke import run
    from invoke.exceptions import UnexpectedExit
except ImportError:
    sys.stderr.write("Please install deployment dependencies to use deploy.\n")
    sys.exit(1)

from ..version import __VERSION__


TS = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")


REQUIRED_BINS = (
    ("python3", ("python3.6", "python-3.6")),
    ("virtualenv", ("virtualenv3.6", "virtualenv-3.6", "virtualenv")),
)


#
# Utils
#


def echo(str):
    sys.stderr.write(str)
    sys.stderr.flush()


def echo_h1(str):
    echo(Fore.YELLOW + Style.BRIGHT + "%s" % str)
    echo("\n")


def echo_h2(str):
    echo(Style.BRIGHT + "%s" % str)
    echo("\n")


def echo_body(str):
    echo("%s" % str)
    echo("\n")


def echo_error(str):
    echo(Fore.RED + "%s" % str)
    echo("\n")


def fail(e, desc=None):
    if not desc:
        desc = "perform the operation"
    echo_error("Could not %s. The error given was:" % desc)
    echo_error("%s" % "\n".join(e.result.stderr.splitlines()))
    sys.exit(1)


def normalize_cmd(cmd):
    if not isinstance(cmd, str):
        cmd = " ".join((shlex.quote(c) for c in cmd))
    return cmd


def run_as(conn, sudo_user, cmd, **kwargs):
    if "shell" not in kwargs:
        kwargs["shell"] = "/bin/sh"
    if sudo_user:
        kwargs["user"] = sudo_user
        return conn.sudo(normalize_cmd(cmd), **kwargs)
    return conn.run(normalize_cmd(cmd), **kwargs)


def run_local(cmd, **kwargs):
    if "shell" not in kwargs:
        kwargs["shell"] = "/bin/sh"
    return run(normalize_cmd(cmd), **kwargs)


#
# Step: readiness check
#


def _check_bin(conn, required_bins, sudo_user=None):
    metadata = {}
    ok = True
    for k, v in required_bins:
        echo("Checking for %s ... " % k)
        detected_bin = None
        for bin in v:
            try:
                run_as(conn, sudo_user, ["hash", bin], hide=True)
                detected_bin = bin
            except UnexpectedExit:
                continue
        if detected_bin:
            echo("found %s\n" % detected_bin)
            metadata[k] = detected_bin
        else:
            echo("not found\n")
            ok = False
    return ok, metadata


def _check_path(conn, path, sudo_user=None):
    echo("Checking if %s is writable " % path)
    if sudo_user:
        echo("by %s " % sudo_user)
    echo("... ")

    tmp_path = os.path.join(path, uuid.uuid4().hex)
    try:
        run_as(conn, sudo_user, ["mkdir", "-p", path], hide=True)
        run_as(conn, sudo_user, ["touch", tmp_path], hide=True)
        run_as(conn, sudo_user, ["rm", tmp_path], hide=True)
    except UnexpectedExit:
        echo("not writable\n")
        return False
    echo("ok\n")
    return True


def check_readiness(args, sudo_user=None):
    echo_h1("Checking readiness")
    success = True
    metadata = {}
    for host in args.host:
        with Connection(host, port=args.port, user=args.user) as conn:
            echo_h2(host)
            ok1, m = _check_bin(conn, REQUIRED_BINS, sudo_user)
            ok2 = _check_path(conn, args.path, sudo_user)
            success = success and ok1 and ok2
            metadata[host] = m
            echo("\n")
    if success:
        return metadata
    echo_error("The system failed readiness check. You may fix this by making sure")
    echo_error("packages are installed and the deploy path is writable by the user.")
    sys.exit(1)


#
# Step: pack
#


def pack_app(args, sudo_user=None):
    echo_h1("Preparing distribution")

    echo("Compiling assets ... ")
    try:
        run_local(["npm", "run", "gulp"], hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        echo_error("Failed to compile assets. The error given was:")
        echo_error("%s" % "\n".join(e.result.stderr.splitlines()))
        sys.exit(1)
    echo("done\n")

    echo("Creating distribution ... ")
    try:
        run_local(["poetry", "build", "--format=sdist"], hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        fail(e, "create distribution")
    echo("done\n\n")


#
# Step: setup
#


def _upload_artifact(conn, local, remote):
    echo("Uploading distribution ... ")
    conn.put(local, remote)
    conn.run(normalize_cmd(["chmod", "0644", remote]), hide=True)
    echo("done\n")


def _extract_artifact(conn, dist, srcdir, sudo_user=None):
    echo("Extracting distribution ... ")
    try:
        run_as(conn, sudo_user, ["mkdir", "-p", srcdir], hide=True)
        run_as(
            conn,
            sudo_user,
            ["tar", "-xvzf", dist, "--strip-components=1", "-C", srcdir],
            hide=True,
        )
        # Unfortunately putting file as deployuser isn't very straightforward.
        # We have to put as the logged in user, and must use the same user to
        # perform the cleanup.
        conn.run(normalize_cmd(["rm", dist]), hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        fail(e, "extract distribution")
    echo("done\n")


def _setup_app(conn, srcdir, hostmeta, sudo_user=None):
    echo("Setting up application ... ")
    try:
        with conn.cd(srcdir):
            run_as(
                conn,
                sudo_user,
                [
                    hostmeta["virtualenv"],
                    "-p",
                    hostmeta["python3"],
                    "--always-copy",
                    "venv",
                ],
                hide=True,
            )
            run_as(conn, sudo_user, ["venv/bin/pip3", "install", "-e", "."], hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        fail(e, "setup application")
    echo("done\n")


def setup_app(args, metadata, sudo_user=None):
    echo_h1("Setting up the application")

    dist = "fanboi2-%s.tar.gz" % __VERSION__
    dist_local = "dist/%s" % dist
    dist_remote = "/tmp/%s-v%s.tar.gz" % (TS, __VERSION__)
    srcdir_remote = "%s/versions/%s-v%s" % (args.path, TS, __VERSION__)
    for host in args.host:
        # Upload session need to be closed before running conn.run
        # otherwise this may result in two SSH connections to the server.
        with Connection(host, port=args.port, user=args.user) as conn:
            echo_h2(host)
            _upload_artifact(conn, dist_local, dist_remote)
        with Connection(host, port=args.port, user=args.user) as conn:
            hostmeta = metadata[host]
            _extract_artifact(conn, dist_remote, srcdir_remote, sudo_user)
            _setup_app(conn, srcdir_remote, hostmeta, sudo_user)
            echo("\n")
    return srcdir_remote


#
# Step: committing
#


def _commit_app(conn, srcdir, current, sudo_user=None):
    echo("Committing changes ... ")
    try:
        run_as(conn, sudo_user, ["ln", "-sfF", srcdir, current], hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        fail(e, "commit changes")
    echo("done\n")


def _commit_postcmd(conn, postcmd, sudo_user=None):
    if postcmd is not None:
        echo("Running post-commit command ... ")
        try:
            run_as(conn, sudo_user, shlex.split(postcmd), hide=True)
        except UnexpectedExit as e:
            echo("failed\n\n")
            fail(e, "perform post-commit command")
        echo("done\n")


def _cleanup_versions(conn, versions, keep, sudo_user=None):
    echo("Cleaning up older versions ... ")

    # Always keep the latest version
    keep += 1
    all_versions = conn.sftp().listdir(versions)
    normalized_versions = [os.path.join(versions, d) for d in sorted(all_versions)]
    deletable_versions = normalized_versions[:-keep]
    try:
        # Using rm -rf since versions may be using different user than
        # the one logged in (when --deployuser is given).
        run_as(conn, sudo_user, ["rm", "-rf", *deletable_versions], hide=True)
    except UnexpectedExit as e:
        echo("failed\n\n")
        fail(e, "cleanup older versions")
    echo("done\n")


def commit_app(args, srcdir, sudo_user=None):
    echo_h1("Committing changes")
    current = "%s/current" % args.path

    versions = os.path.abspath(os.path.join(srcdir, ".."))

    for host in args.host:
        with Connection(host, port=args.port, user=args.user) as conn:
            echo_h2(host)
            _commit_app(conn, srcdir, current, sudo_user)
            _commit_postcmd(conn, args.postcmd, sudo_user)
            _cleanup_versions(conn, versions, args.keep, sudo_user)
        echo("\n")


def deploy(args):
    sudo_user = None
    if args.user != args.deployuser:
        sudo_user = args.deployuser

    metadata = check_readiness(args, sudo_user)
    pack_app(args, sudo_user)
    srcdir = setup_app(args, metadata, sudo_user)
    commit_app(args, srcdir, sudo_user)


def main():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, nargs="+")
    parser.add_argument("--user", type=str, default=getpass.getuser())
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--keep", type=int, default=3)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--deployuser", type=str, default=None)
    parser.add_argument("--postcmd", type=str, default=None)

    args = parser.parse_args()
    if args.host is None:
        parser.print_usage()
        sys.exit(1)

    if args.deployuser is None:
        args.deployuser = args.user

    init(autoreset=True)
    deploy(args)
