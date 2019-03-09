#!/bin/sh

## Utils
##

echo_clear() {
    printf "\\033[1A\\r\\033[K"
}

echo_newline() {
    printf "\\n"
}

echo_ok() {
    printf "=> \\033[1;37m%s\\033[0;0m\\n" "$1"
}

echo_wait() {
    printf "=> \\033[0;33m%s\\033[0;0m\\n" "$1"
}

echo_error() {
    printf "=> \\033[0;31m%s\\033[0;0m\\n" "$1"
}

echo_info() {
    printf "   \\033[0;36m%s\\033[0;0m\\n" "$1"
}


## Sanity check
##

echo_wait "Checking system..."

if [ "$(uname)" != "FreeBSD" ]; then
    echo_error "Development environment setup script only supports FreeBSD."
    echo_info "For other operating systems, please see README.md."
    exit 1
fi

if [ "$(id -u)" != "0" ] || [ -z "$SUDO_USER" ]; then
    echo_error "Must be run with sudo."
    echo_info "If this was run over SSH, the correct command should be:"
    echo_info "cat builds/bsd-bootstrap.sh | ssh host sudo sh"
    exit 1
fi

LOGIN_USER=$SUDO_USER


## Ports
##

if [ -f "/usr/ports/Makefile" ]; then
    echo_ok "FreeBSD Ports already exists."
else
    echo_wait "Development setup script requires FreeBSD Ports. Fetching..."
    portsnap auto
fi

if hash synth 2>&1; then
    echo_ok "Synth is already installed."
else
    echo_wait "Synth is not installed. Installing..."
    make -C /usr/ports/ports-mgmt/synth install clean
fi


## Installation
##

mkdir -p /usr/local/etc/synth/
echo_wait "Configuring Synth..."

if [ -f /usr/local/etc/synth/LiveSystem-make.conf ]; then
    echo_info "Configuration for LiveSytem already exists at /usr/local/etc/synth."
    echo_info "Moving LiveSystem-make.conf into LiveSystem-make.conf.bak"
    mv /usr/local/etc/synth/LiveSystem-make.conf /usr/local/etc/synth/LiveSystem-make.conf.bak
fi

cat <<EOF > /usr/local/etc/synth/LiveSystem-make.conf
DEFAULT_VERSIONS+=ssl=libressl

# ftp/curl
ftp_curl_UNSET+=GSSAPI_NONE TLS_SRP
ftp_curl_SET+=GSSAPI_HEIMDAL

# security/p5-GSSAPI <- ftp/curl
security_p5-GSSAPI_UNSET+=GSSAPI_BASE
security_p5-GSSAPI_SET+=GSSAPI_HEIMDAL

# www/node8
www_node8_SET+=BUNDLED_SSL

# www/yarn
www_yarn_UNSET+=NODE
www_yarn_SET+=NODE8
EOF

INSTALL_LIST="$(mktemp)"
trap 'rm $INSTALL_LIST' 0 1 2 3 6 14 15

cat <<EOF > "$INSTALL_LIST"
databases/postgresql10-server
databases/py-sqlite3@py36
databases/redis
databases/sqlite3
devel/git-lite
devel/py-pip@py36
devel/py-virtualenv@py36
ftp/curl
graphics/GraphicsMagick
lang/python36
net/openntpd
security/ca_root_nss
www/node8
www/npm-node8
www/yarn
EOF

echo_wait "Installing development dependencies..."
echo_info "This may take a (really) long time."

# Redirecting STDIN otherwise Synth will cause the rest of
# shell script to broke for some reason...
synth install "$INSTALL_LIST" </dev/null


## Enabling services
##

if service openntpd onestatus >/dev/null; then
    echo_ok "OpenNTPd is already enabled."
else
    echo_wait "Enabling OpenNTPd..."
    sysrc openntpd_enable=YES
    service openntpd start
fi

if service postgresql onestatus >/dev/null; then
    echo_ok "PostgreSQL is already enabled."
else
    echo_wait "Enabling PostgreSQL..."
    service postgresql oneinitdb

    # Note: pg_ctl will write its output to controlling terminal which
    # will cause shell process to never terminate. See also pg_ctl(1).
    sysrc postgresql_enable=YES
    sysrc postgresql_flags="-l /var/log/postgresql.log"

    touch /var/log/postgresql.log
    chown postgres:postgres /var/log/postgresql.log

    cat <<EOF > /var/db/postgres/data10/pg_hba.conf
local all all trust
host all all 127.0.0.1/32 trust
host all all ::1/128 trust
EOF

    service postgresql start
    sudo -u postgres createuser -ds "$LOGIN_USER" || true
    sudo -u postgres createuser -ds fanboi2 || true
fi

if service redis onestatus >/dev/null; then
    echo_ok "Redis is already enabled."
else
    echo_wait "Enabling Redis..."
    sysrc redis_enable=YES
    service redis start
fi

# nfsclient doesn't provide status so we're checking
# the lock daemon instead.
if service lockd onestatus >/dev/null; then
    echo_ok "NFS is already enabled."
else
    echo_wait "Enabling NFS..."
    sysrc nfs_client_enable=YES
    sysrc rpc_lockd_enable="YES"
    sysrc rpc_statd_enable="YES"
    service nfsclient start
    service lockd start
    service statd start
fi


## User configurations
##

echo_wait "Setting up user environment..."
echo_info "You must setup NFS mount and run \`make devserver\` on your own."
echo_info "However initial configuration will be provided at .local/fanboi2/env"
echo_info "with ENVFILE configured."

sudo -u "$LOGIN_USER" sh <<EOF
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

# Fanboi2
FBVAR=\$HOME/.local/fanboi2; export FBVAR
VIRTUALENV=virtualenv-3.6; export VIRTUALENV
BUILDDIR=\\\$FBVAR/build; export BUILDDIR
VENVDIR=\\\$FBVAR/venv; export VENVDIR
ENVFILE=\\\$FBVAR/env; export ENVFILE
PATH=\\\$VENVDIR/bin:\\\$PATH; export PATH
EOPROFILE

. "\$HOME/.profile"
mkdir -p \$FBVAR

cat <<EOENV > "\$ENVFILE"
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
DATABASE_URL=postgresql://fanboi2:@127.0.0.1:5432/fanboi2_dev
POSTGRESQL_TEST_DATABASE=postgresql://fanboi2:@127.0.0.1:5432/fanboi2_test
REDIS_URL=redis://127.0.0.1:6379/0
SERVER_DEV=true
SERVER_HOST=0.0.0.0
SERVER_PORT=6543
SESSION_SECRET=\$(openssl rand -hex 32)
AUTH_SECRET=\$(openssl rand -hex 32)
EOENV
EOF

(
    psql -U fanboi2 template1 -c "CREATE DATABASE fanboi2_dev;" || true
    psql -U fanboi2 template1 -c "CREATE DATABASE fanboi2_test;" || true
) >/dev/null 2>&1
