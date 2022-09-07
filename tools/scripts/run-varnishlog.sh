#!/bin/sh
set -e

BASE_DIR=$(
    cd "$(dirname "$0")" || exit 1
    pwd -P
)
DATA_DIR="$BASE_DIR/../../tmp/varnish"

init_varnish() {
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
    fi
}

start_varnishlog() {
    exec varnishlog -n "$DATA_DIR" "$@"
}

init_varnish
start_varnishlog "$@"
