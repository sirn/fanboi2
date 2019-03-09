FROM node:8-alpine as assets

WORKDIR /src

COPY Makefile gulpfile.js package.json tsconfig.json yarn.lock ./
COPY assets ./assets

RUN set -xe \
 && apk add --update --no-cache --virtual .run-deps \
        make \
 && make assets

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

ENV HOME /data

ENV DATADIR /data
ENV VENVDIR /data/venv
ENV BUILDDIR /data/build

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
 && addgroup -g 10000 fanboi2 \
 && adduser -D -h /tmp -u 10000 -G fanboi2 fanboi2 \
 && mkdir -p $DATADIR \
 && chown -R "10000:10000" $DATADIR \
 && chown -R "10000:10000" /src \
 && s6-setuidgid fanboi2 make prod \
 && rm -rf /data/.cache \
 && apk del .app-build

COPY rootfs/ /
COPY --chown=fanboi2:fanboi2 alembic.ini ./
COPY --chown=fanboi2:fanboi2 fanboi2/ ./fanboi2
COPY --chown=fanboi2:fanboi2 migration/ ./migration
COPY --chown=fanboi2:fanboi2 --from=assets /src/fanboi2/static ./fanboi2/static

RUN set -xe \
 && chmod +x /entrypoint

ENTRYPOINT ["/init", "/entrypoint"]

CMD ["serve"]
