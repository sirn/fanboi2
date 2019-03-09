#!/bin/sh

gen_cache() {
    _name=$1; shift
    _hashfile=$1; shift

    if [ -z "$_name" ] || [ -z "$_hashfile" ]; then
        printf "Usage: gen_cache name hashfile\\n" >&2
        return 1
    fi

    if [ ! -e "$_hashfile" ]; then
        printf "%s could not be found. Skipping gen cache.\\n" "$_hashfile" >&2
        return 1
    fi

    _hash=$(openssl dgst -sha256 -r "$_hashfile" | awk '{ print $1 }')
    printf "%s-%s.tar.gz" "$_name" "$_hash"
}


restore_cache() {
    _bucket=$1; shift
    _chdir=$1; shift
    _name=$1; shift
    _hashfile=$1; shift

    if [ -z "$_bucket" ] || [ -z "$_name" ] || [ -z "$_hashfile" ]; then
        printf "Usage: restore_cache bucket chdir name hashfile\\n" >&2
        return 1
    fi

    if ! _cachefile=$(gen_cache "$_name" "$_hashfile"); then return 1; fi
    if ! gsutil stat "$_bucket/$_cachefile" 2>/dev/null; then return 1; fi

    gsutil cp "$_bucket/$_cachefile" "/tmp/$_cachefile" 2>/dev/null
    tar -xzf "/tmp/$_cachefile" -C "$_chdir"
    rm "/tmp/$_cachefile"
}


store_cache() {
    _bucket=$1; shift
    _chdir=$1; shift
    _name=$1; shift
    _hashfile=$1; shift

    if [ -z "$_bucket" ] || [ -z "$_name" ] || [ -z "$_hashfile" ]; then
        printf "Usage: store_cache bucket chdir name hashfile path...\\n" >&2
        return 1
    fi

    if ! _cachefile=$(gen_cache "$_name" "$_hashfile"); then return 1; fi
    if gsutil stat "$_bucket/$_cachefile" 2>/dev/null; then return 0; fi

    # shellcheck disable=SC2068
    tar -czf "/tmp/$_cachefile" -C "$_chdir" $@
    gsutil cp "/tmp/$_cachefile" "$_bucket/$_cachefile" 2>/dev/null
}


wait_file() {
    _file=$1; shift
    _timeout=$1; shift

    while [ "$_timeout" -gt 0 ]; do
        [ -e "$_file" ] && return
        sleep 1
        _timeout=$((_timeout-1))
    done

    return 1
}
