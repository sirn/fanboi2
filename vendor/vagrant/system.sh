#!/bin/sh
sysrc hostname=vagrant
hostname vagrant

pkg update
pkg install -y \
    bzip2 \
    ca_root_nss \
    curl \
    git-lite \
    gmake \
    memcached \
    node8 \
    npm-node8 \
    ntp \
    postgresql10-server \
    py36-pip \
    py36-sqlite3 \
    py36-virtualenv \
    python36 \
    redis \
    sqlite3 \
    sudo

npm install -g yarn

sysrc \
    ntpd_enable=YES \
    ntpd_enable=YES \
    postgresql_enable=YES \
    redis_enable=YES \
    memcached_enable=YES

ntpd -qg

service ntpd start
service postgresql initdb
service postgresql start
service redis start
service memcached start

cat <<EOF | tee /var/db/postgres/data10/pg_hba.conf
local all all trust
host all all 127.0.0.1/32 trust
host all all ::1/128 trust
EOF

sudo -u postgres createuser -ds vagrant || true
sudo -u postgres createuser -ds fanboi2 || true
service postgresql restart

chsh -s /bin/sh vagrant
