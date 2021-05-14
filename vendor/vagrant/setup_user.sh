#!/bin/sh
#
# Setting up (user).
#

set -e

T_BOLD=$(tput bold 2>/dev/null || true)
T_RESET=$(tput sgr0 2>/dev/null || true)

printe() {
    printf "%s\\n" "$@"
}

printe_h1() {
    printf -- "==> %s%s%s\\n" "$T_BOLD" "$@" "$T_RESET"
}

printe_h2() {
    printf -- "--> %s\\n" "$@"
}

## Initial configuration
## ----------------------------------------------------------------------------

printe_h1 "Cleaning up home..."

cd "$HOME" || exit 1
cat <<EOF | xargs rm -f
.bashrc
.cshrc
.lesshst
.login
.login-e
.login_conf
.mail_aliases
.mailrc
.profile
.profile-e
.rhosts
.rnd
.shrc
EOF

## Setup Profile
## ----------------------------------------------------------------------------

printe_h1 "Setting up profile..."

cat <<EOF > "$HOME/.profile"
EDITOR=vim; export EDITOR
PAGER=more; export PAGER
LANG=en_US.UTF-8; export LANG
PATH=\$PATH:\$HOME/.local/bin:\$HOME/.venv/bin; export PATH
EOF

# shellcheck disable=SC1090,SC1091
. "$HOME/.profile"

## Python Venv
## ----------------------------------------------------------------------------

printe_h1 "Preparing Python venv..."

if [ ! -d "$HOME/.venv" ]; then
    /usr/local/bin/python3.8 -m venv "$HOME/.venv"
fi

if [ ! -f "$HOME/.venv/bin/pip3" ]; then
    "$HOME/.venv/bin/python3" -m ensurepip
fi

if [ ! -f "$HOME/.venv/bin/poetry" ]; then
    "$HOME/.venv/bin/pip3" install poetry
fi

## Nodejs
## ----------------------------------------------------------------------------

printe_h1 "Preparing Nodejs..."

npm set prefix="$HOME/.local"
if [ ! -f "$HOME/.local/bin/pnpm" ]; then
    npm install -g pnpm
fi

## Prepare application
## ----------------------------------------------------------------------------

printe_h1 "Setting up application..."

cd /vagrant || exit 1

psql template1 -c "CREATE DATABASE fanboi2_dev;" || true
psql template1 -c "CREATE DATABASE fanboi2_test;" || true

"$HOME/.venv/bin/poetry" install || exit 1
# "$HOME/.local/bin/pnpm" install || exit 1
# "$HOME/.local/bin/pnpm" run gulp || exit 1

## Configure application
## ----------------------------------------------------------------------------

if [ ! -f /vagrant/.env ]; then
    print_h1 "Configuring application..."

    cat <<EOF > "/vagrant/.env"
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
DATABASE_URL=postgresql://vagrant:@127.0.0.1:5432/fanboi2_dev
REDIS_URL=redis://127.0.0.1:6379/0
SERVER_DEV=true
SERVER_HOST=0.0.0.0
SERVER_PORT=6543
SESSION_SECRET=\$(openssl rand -hex 32)
AUTH_SECRET=\$(openssl rand -hex 32)
EOF
fi
