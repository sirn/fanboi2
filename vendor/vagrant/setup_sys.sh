#!/bin/sh
#
# Setting up system.
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

if [ "$(hostname)" != "vagrant" ]; then
    printe_h1 "Setting up hostname..."
    sysrc hostname=vagrant
    hostname vagrant
fi

# generic/freebsd12 image ship with broken rc.conf, i.e. use `firstboot-growfs`
# instead of `firstboot_growfs`, causing lots of warnings when running pkg.
if grep -q ^firstboot /etc/rc.conf; then
    printe_h1 "Removing invalid rc.conf..."

    if awk '! /^firstboot/' < /etc/rc.conf > /etc/rc.conf.tmp; then
        mv /etc/rc.conf.tmp /etc/rc.conf
    fi
fi

## Packages
## ----------------------------------------------------------------------------

if grep -q "url:.*/quarterly" /etc/pkg/FreeBSD.conf; then
    printe_h1 "Switching pkgs to latest..."
    sed -i '' 's|\(url:.*\/\)quarterly"|\1latest"|' /etc/pkg/FreeBSD.conf
fi

printe_h1 "Updating packages, this may take a while..."
pkg upgrade -qy
pkg update -qf

printe_h1 "Installing packages..."
cat <<EOF | xargs pkg install -y
bzip2
ca_root_nss
curl
git-lite
gmake
node14
npm-node14
ntp
postgresql11-client
postgresql11-server
py38-pip
py38-sqlite3
python38
redis
sqlite3
sudo
EOF

## Services: ntpd
## ----------------------------------------------------------------------------

if ! service ntpd onestatus >/dev/null; then
    printe_h1 "Enabling ntpd..."

    sysrc ntpd_enable=YES
    ntpd -qg
    service ntpd start
fi

## Services: postgresql
## ----------------------------------------------------------------------------

if ! service postgresql onestatus >/dev/null; then
    printe_h1 "Enabling PostgreSQL..."

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

## Services: redis
## ----------------------------------------------------------------------------

if ! service redis onestatus >/dev/null; then
    printe_h1 "Enabling Redis..."

    sysrc redis_enable=YES
    service redis start
fi

## User setup
## ----------------------------------------------------------------------------

printe_h1 "Setting up user..."

chsh -s /bin/sh vagrant
