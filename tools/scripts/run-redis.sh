#!/bin/sh
set -e

BASE_DIR=$(cd "$(dirname "$0")" || exit 1; pwd -P)
DATA_DIR="$BASE_DIR/../../tmp/redis"

init_redis() {
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
    fi
}

start_redis() {
    exec redis-server
}

init_redis
start_redis
