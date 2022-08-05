#!/bin/sh -e
#
# Update version in pyproject.toml and package.json
#

BASE_DIR=$(cd "$(dirname "$0")/../../" || exit 1; pwd -P)
cd "$BASE_DIR/" || exit 1

if [ $# -lt 1 ]; then
    echo >&2 "Usage: $(basename "$0") NEW_VERSION"
    exit 2
fi

NEW_VERSION=$1
NEW_VERSION=${NEW_VERSION##v}

if test -f pyproject.toml; then
    PEP440_VERSION=${NEW_VERSION%%-*}
    PEP440_LOCAL=${NEW_VERSION##"$PEP440_VERSION"-}

    LOCAL1=${PEP440_LOCAL%%-*}
    if [ -n "$LOCAL1" ]; then
        PEP440_VERSION="${PEP440_VERSION}+$LOCAL1"
        LOCAL1_REST=${PEP440_LOCAL##"$LOCAL1"-}
    fi

    LOCAL2=${LOCAL1_REST%%-*}
    if [ -n "$LOCAL2" ] && [ "$LOCAL2" != "$LOCAL1" ]; then
        PEP440_VERSION="${PEP440_VERSION}.git.${LOCAL2}"
        LOCAL2_REST=${LOCAL1_REST##"$LOCAL2"-}
    fi

    LOCAL3=${LOCAL2_REST%%-*}
    if [ -n "$LOCAL3" ] && [ "$LOCAL3" != "$LOCAL2" ]; then
        PEP440_VERSION="${PEP440_VERSION}.${LOCAL3}"
    fi

    echo >&2 "Updating pyproject.toml version to $PEP440_VERSION"

    awk -v version="$PEP440_VERSION" '
        m = match($0, "^([ ]*version[ ]*=[ ]+)") {
            print substr($0, RSTART, RLENGTH) "\"" version "\""
        } ! m { print }
    ' < pyproject.toml > pyproject.toml.new
    mv pyproject.toml.new pyproject.toml
fi

if test -f package.json; then
    echo >&2 "Updating package.json version to $NEW_VERSION"
    awk -v version="$NEW_VERSION" '
        m = match($0, "^([ ]*\"version\":[ ]*)") {
            print substr($0, RSTART, RLENGTH) "\"" version "\","
        } ! m { print }
    ' < package.json > package.json.new
    mv package.json.new package.json
fi
