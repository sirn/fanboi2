FROM node:8-alpine as assets

WORKDIR /src

COPY Makefile gulpfile.js package.json tsconfig.json yarn.lock ./
COPY assets ./assets

RUN set -xe \
 && apk add --update --no-cache --virtual .assets-build \
        make \
 && make assets \
 && apk del .assets-build

FROM python:3.6-alpine

ENV S6_VERSION 1.21.7.0

RUN set -xe \
 && apk add --update --no-cache --virtual .s6-fetch \
        ca-certificates \
        curl \
 && S6_DOWNLOAD_URL="https://github.com/just-containers/s6-overlay/releases/download/v${S6_VERSION}/s6-overlay-amd64.tar.gz" \
 && S6_DOWNLOAD_SHA256="7ffd83ad59d00d4c92d594f9c1649faa99c0b87367b920787d185f8335cbac47" \
 && curl -fsL -o s6-overlay.tar.gz "${S6_DOWNLOAD_URL}" \
 && echo "${S6_DOWNLOAD_SHA256}  s6-overlay.tar.gz" |sha256sum -c - \
 && tar -xzC / -f s6-overlay.tar.gz \
 && rm s6-overlay.tar.gz \
 && apk del .s6-fetch

ENV HOME /tmp
ENV VENVDIR /venv
ENV BUILDDIR /build

WORKDIR /src

COPY Makefile setup.py setup.cfg ./

RUN set -xe \
 && apk add --update --no-cache --virtual .app-build \
        build-base \
        libffi-dev \
        postgresql-dev \
        py3-virtualenv \
 && apk add --update --no-cache --virtual .app-run \
        libffi \
        make \
        postgresql-libs \
 && sed -i -e 's/^all:*/all: prod/' Makefile \
 && sed -i -e 's/^ASSETS_SRCS.*/ASSETS_SRCS ?=/' Makefile \
 && make prod \
 && rm -rf /tmp/.cache \
 && apk del .app-build

COPY alembic.ini ./
COPY fanboi2/ ./fanboi2
COPY migration/ ./migration

COPY --from=assets /src/fanboi2/static ./fanboi2/static

COPY vendor/rootfs/ /

ARG user=fanboi2
ARG group=fanboi2
ARG uid=10000
ARG gid=10000

RUN set -xe \
 && addgroup -g ${gid} ${group} \
 && adduser -D -h /tmp -u ${uid} -G ${group} ${user}
 && chown -R "${uid}:${gid}" /build \
 && chown -R "${uid}:${gid}" /src \
 && chown -R "${uid}:${gid}" /venv \
 && chmod +x /entrypoint

ENTRYPOINT ["/init", "/entrypoint"]

CMD ["serve"]
