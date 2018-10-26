#!/bin/sh

## User profiles
##

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

cat <<EOF | tee "$HOME/.profile"
EDITOR=vim; export EDITOR
PAGER=more; export PAGER
LANG=en_US.UTF-8; export LANG
EOF


## Work directory
##

cd /vagrant || exit

psql template1 -c "CREATE DATABASE fanboi2_dev;"
psql template1 -c "CREATE DATABASE fanboi2_test;"

cat <<ENV | tee "/vagrant/.env"
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
DATABASE_URL=postgresql://vagrant:@127.0.0.1:5432/fanboi2_dev
MEMCACHED_URL=127.0.0.1:11211
REDIS_URL=redis://127.0.0.1:6379/0
SERVER_DEV=true
SERVER_HOST=0.0.0.0
SERVER_PORT=6543
SESSION_SECRET=$(openssl rand -hex 32)
AUTH_SECRET=$(openssl rand -hex 32)
ENV


## Application
##

VIRTUALENV=virtualenv-3.6 make -j2 dev migrate
