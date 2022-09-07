#!/bin/sh
set -e

BASE_DIR=$(
    cd "$(dirname "$0")" || exit 1
    pwd -P
)
DATA_DIR="$BASE_DIR/../../tmp/varnish"

VARNISH_MEM=${VARNISH_MEM:-64M}
VARNISH_LISTEN=${VARNISH_LISTEN:-0.0.0.0:6544}
VARNISH_MGMT_LISTEN=${VARNISH_MGMT_LISTEN:-127.0.0.1:16544}

init_varnish() {
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
    fi
}

start_varnish() {
    exec varnishd -F -n "$DATA_DIR" -s malloc,"$VARNISH_MEM" -j none -a "$VARNISH_LISTEN" -T "$VARNISH_MGMT_LISTEN" -f "$BASE_DIR/../varnish/main.vcl"
}

init_varnish
start_varnish
