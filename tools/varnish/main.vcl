vcl 4.1;

import std;
import directors;
import cookie;

backend backend1 {
    .host = "127.0.0.1";
    .port = "6543";
    .probe = {
        .url = "/";
        .interval = 5s;
        .timeout = 30s;
        .window = 5;
        .threshold = 3;
    }
}

sub vcl_init {
    new app = directors.round_robin();
    app.add_backend(backend1);
}

sub vcl_recv {
    set req.backend_hint = app.backend();

    # Allow purges
    if (req.method == "PURGE") {
        return (purge);
    }

    # Varnish is public-facing, always override X-Forwarded-For.
    set req.http.x-forwarded-for = client.ip;
    set req.http.x-forwarded-proto = "http";

    # Do nothing for non-GET/non-HEAD.
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # DO nothing for non-RFC request methods.
    if (req.method != "GET" &&
            req.method != "HEAD" &&
            req.method != "PUT" &&
            req.method != "POST" &&
            req.method != "TRACE" &&
            req.method != "OPTIONS" &&
            req.method != "PATCH" &&
            req.method != "DELETE") {
        return (pipe);
    }

    # Normalize requests
    set req.url = std.querysort(req.url);
    unset req.http.proxy;

    # Remove trailing # as we should never see it.
    if (req.url ~ "\#") {
        set req.url = regsub(req.url, "\#.*$", "");
    }

    # Normalize Accept-Encoding header
    if (req.url ~ "\.(jpg|png|gif|gz|tgz|bz2|tbz|mp3|ogg)$") {
        # No point in compressing these
        unset req.http.accept-encoding;
    } elsif (req.http.accept-encoding ~ "gzip") {
        set req.http.accept-encoding = "gzip";
    } elsif (req.http.accept-encoding ~ "deflate") {
        set req.http.accept-encoding = "deflate";
    } else {
        unset req.http.accept-encoding;
    }

    # Normalize Accept-Language header (e.g. we don't do this)
    unset req.http.accept-language;

    # Strip a trailing ? in the URL.
    if (req.url ~ "\?$") {
        set req.url = regsub(req.url, "\?$", "");
    }

    # Cleanup cookies.
    cookie.parse(req.http.cookie);
    cookie.keep("_auth,_session,_theme");
    set req.http.cookie = cookie.get_string();

    # Announce ESI support to the backend.
    set req.http.surrogate-capability = "key=ESI/1.0";

    # Never cache authorization.
    if (req.http.authorization) {
        return (pass);
    }

    # Never cache admin.
    if (req.url ~ "^/admin(/.*)?") {
        return (pass);
    }

    # Never cache task API.
    if (req.url ~ "^/api/1\.0/tasks(/.*)?") {
        return (pass);
    }

    # Cannot cache post pages
    if (req.url ~ "^/([^/]+)/[0-9]+/?") {
        if (req.url !~ "^/api/") {
            return (pass);
        }
    }

    return (hash);
}

sub vcl_hash {
    if (req.url !~ "^/api/1\.0(/.*)?") {
        hash_data(cookie.get("_theme"));
    }
}

sub vcl_backend_response {
    set beresp.ttl = 10s;
    set beresp.grace = 3s;

    if (beresp.http.surrogate-control ~ "ESI/1.0") {
         unset beresp.http.surrogate-control;
         set beresp.do_esi = true;
    }

    # Enforce Gzip for any Gzippable content (HTML, CSS, JavaScript, etc.)
    if (beresp.http.content-type ~ "text|javascript") {
        set beresp.do_gzip = true;
    }

    if (bereq.url ~ "^[^?]*\.(css|js|png|ico)(\?.*)?$") {
        set beresp.ttl = 60m;
        set beresp.grace = 3m;
    } elseif (bereq.url ~ "^/pages/") {
        set beresp.ttl = 60m;
        set beresp.grace = 3m;
    } elseif (bereq.url ~ "^/api/1\.0/topics/([^/]+)/posts/([0-9]+)/") {
        set beresp.ttl = 30m;
        set beresp.grace = 1m;
    } elseif (bereq.url ~ "^/$") {
        set beresp.ttl = 10m;
        set beresp.grace = 1m;
    }
}

sub vcl_deliver {
    # Enforce Cache-Control header for CSS/JS/PNG/ICO files.
    if (req.url ~ "^[^?]*\.(css|js|png|ico)(\?.*)?$") {
        set resp.http.cache-control = "public, max-age=31536000, stale-while-revalidate=3";
    }
}