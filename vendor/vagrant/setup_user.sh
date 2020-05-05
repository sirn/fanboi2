#!/bin/sh
#
# Setting up user.
#

set -e


## Utils
##

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


## Cleanup
##

printe_h1 "Cleaning up home..."

cd "$HOME" || exit

rm -f \
   .bashrc \
   .cshrc \
   .lesshst \
   .login \
   .login-e \
   .login_conf \
   .mail_aliases \
   .mailrc \
   .profile \
   .profile-e \
   .rhosts \
   .rnd \
   .shrc


## Setup Profile
##

if [ ! -f "$HOME/.profile" ]; then
    printe_h1 "Setting up profile..."

    cat <<EOPROFILE > "$HOME/.profile"
EDITOR=vim; export EDITOR
PAGER=more; export PAGER
LANG=en_US.UTF-8; export LANG
PATH=\$PATH:\$HOME/.venv/bin; export PATH
EOPROFILE
fi

# shellcheck disable=SC1090
. "$HOME/.profile"


## Prepare Python
##

printe_h1 "Preparing Python environment..."

if [ ! -d "$HOME/.venv" ]; then
    python3.7 -m venv "$HOME/.venv"
fi

if [ ! -f "$HOME/.venv/bin/poetry" ]; then
    pip3 install poetry
fi


## Prepare application
##

printe_h1 "Setting up application..."

cd /vagrant || exit

psql template1 -c "CREATE DATABASE fanboi2_dev;" || true
psql template1 -c "CREATE DATABASE fanboi2_test;" || true

if [ ! -f /vagrant/.env ]; then
    cat <<EOENV > "/vagrant/.env"
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
DATABASE_URL=postgresql://vagrant:@127.0.0.1:5432/fanboi2_dev
REDIS_URL=redis://127.0.0.1:6379/0
SERVER_DEV=true
SERVER_HOST=0.0.0.0
SERVER_PORT=6543
SESSION_SECRET=\$(openssl rand -hex 32)
AUTH_SECRET=\$(openssl rand -hex 32)
EOENV
fi

poetry install || exit 1
npm install || exit 1
npm run gulp || exit 1
