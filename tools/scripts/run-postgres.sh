#!/bin/sh
set -e

BASE_DIR=$(cd "$(dirname "$0")" || exit 1; pwd -P)
DATA_DIR="$BASE_DIR/../../tmp/pgdata"
INIT_USERDB=${INIT_USERDB:-0}

init_postgres() {
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
        pg_ctl initdb -D "$DATA_DIR"
        INIT_USERDB=1
    fi
}

init_userdb() {
    if [ "$INIT_USERDB" = "1" ]; then
        pg_ctl -D "$DATA_DIR" start

        psql --username="$USER" postgres <<-EOF
CREATE USER fanboi2;
CREATE DATABASE fanboi2_dev OWNER fanboi2;
CREATE DATABASE fanboi2_test OWNER fanboi2;
EOF

        pg_ctl -D "$DATA_DIR" stop
    fi
}

start_postgres() {
    cd "$DATA_DIR"
    exec postgres -D "$DATA_DIR"
}

init_postgres
init_userdb
start_postgres
