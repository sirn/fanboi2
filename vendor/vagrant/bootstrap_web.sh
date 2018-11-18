#!/bin/sh
set -xe

sysrc hostname=vagrant
hostname vagrant

# generic/freebsd11 image ship with broken rc.conf, i.e. use `firstboot-growfs`
# instead of `firstboot_growfs`, causing lots of warnings when running pkg.
if awk '! /^firstboot/' < /etc/rc.conf > /etc/rc.conf.tmp; then
    mv /etc/rc.conf.tmp /etc/rc.conf
fi

pkg update -qf

PACKAGES="bzip2 ca_root_nss curl git-lite gmake ntp sqlite3 sudo"
PACKAGES="$PACKAGES postgresql10-server redis"
PACKAGES="$PACKAGES python36 py36-pip py36-sqlite3 py36-virtualenv"
PACKAGES="$PACKAGES node8 npm-node8"

# shellcheck disable=SC2086
pkg install -qy $PACKAGES
npm install -g yarn

if ! service ntpd onestatus >/dev/null; then
    sysrc ntpd_enable=YES
    ntpd -qg
    service ntpd start
fi

if ! service postgresql onestatus >/dev/null; then
    sysrc postgresql_enable=YES

    service postgresql initdb
    cat <<EOF > /var/db/postgres/data10/pg_hba.conf
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
EOPROFILE

cd /vagrant || exit

psql template1 -c "CREATE DATABASE fanboi2_dev;"
psql template1 -c "CREATE DATABASE fanboi2_test;"

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

VIRTUALENV=virtualenv-3.6 make -j$(sysctl -n hw.ncpu) assets dev
EOF
