#!/bin/sh
set -xe

sysrc hostname=vagrant
hostname vagrant

# generic/freebsd12 image ship with broken rc.conf, i.e. use `firstboot-growfs`
# instead of `firstboot_growfs`, causing lots of warnings when running pkg.
if awk '! /^firstboot/' < /etc/rc.conf > /etc/rc.conf.tmp; then
    mv /etc/rc.conf.tmp /etc/rc.conf
fi

pkg upgrade -qy
pkg update -qf

# shellcheck disable=SC2086
pkg install -qy \
    bzip2 \
    ca_root_nss \
    curl \
    git-lite \
    gmake \
    node12 \
    npm-node12 \
    ntp \
    postgresql11-client \
    postgresql11-server \
    py37-pip \
    py37-sqlite3 \
    python37 \
    redis \
    sqlite3 \
    sudo

if ! service ntpd onestatus >/dev/null; then
    sysrc ntpd_enable=YES
    ntpd -qg
    service ntpd start
fi

if ! service postgresql onestatus >/dev/null; then
    sysrc postgresql_enable=YES

    service postgresql initdb
    cat <<EOF > /var/db/postgres/data11/pg_hba.conf
local all all trust
host all all 127.0.0.1/32 trust
host all all ::1/128 trust
EOF

    service postgresql start
    sudo -u postgres createuser -ds vagrant || true
    sudo -u postgres createuser -ds fanboi2 || true
fi

if ! service redis onestatus >/dev/null; then
    sysrc redis_enable=YES
    service redis start
fi

chsh -s /bin/sh vagrant
sudo -u vagrant sh <<EOF
cd "\$HOME" || exit
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

cat <<EOPROFILE > "\$HOME/.profile"
EDITOR=vim; export EDITOR
PAGER=more; export PAGER
LANG=en_US.UTF-8; export LANG
PATH=\$PATH:\$HOME/.venv/bin; export PATH
EOPROFILE

. "\$HOME/.profile"

if [ ! -d "\$HOME/.venv" ]; then
    python3.7 -m venv \$HOME/.venv
fi

pip3 install poetry

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
EOF
