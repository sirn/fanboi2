#!/bin/sh
set -e

BASE_DIR=$(
    cd "$(dirname "$0")" || exit 1
    pwd -P
)
DATA_DIR="$BASE_DIR/../../tmp/varnish"

VARNISH_MGMT_LISTEN=${VARNISH_MGMT_LISTEN:-127.0.0.1:16544}

init_varnish() {
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
    fi
}

start_varnishadm() {
    exec varnishadm \
        -S "$DATA_DIR"/_.secret \
        -T "$VARNISH_MGMT_LISTEN" \
        "$@"
}

init_varnish
start_varnishadm "$@"
