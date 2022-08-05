#!/bin/sh -e
#
# Generates a version number for use in e.g. tags.
#

BASE_DIR=$(cd "$(dirname "$0")/../../" || exit 1; pwd -P)
cd "$BASE_DIR/" || exit 1

# If tag exists, let Git generates the version number in the format of
# `1.1.0-5-e8df964a` where `1.1.0` is the latest tag with common ancestor
# as this commit, `5` is number of commits since the tag, and `e8df964a`
# being the rev of the latest commit.
#
VERSION=$(git describe --tags --long --dirty 2>/dev/null)

if [ -n "$VERSION" ]; then
    echo "$VERSION"
    exit
fi

# If tag doesn't exist and worktree isn't dirty, we try to replicate the
# same format with `0.0.0-0-e8df964a` where `e8df964a` is the rev of the
# latest commit.
#
REV=$(git rev-parse --short HEAD 2>/dev/null)

if [ -n "$REV" ]; then
    echo "v0.0.0-0-$REV"
    exit
fi

# Everything fails, use `0.0.0-dev`
#
echo "v0.0.0-0"
