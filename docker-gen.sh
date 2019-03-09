#!/bin/sh

set -e

## Arguments handling
##

print_usage() {
    printf "Usage: %s [CONFIG...] [OPTS...]\\n" "$0"
    printf "\\n"
    printf "OPTS:\\n"
    printf "\\n"
    printf "     -h                      Print this help.\\n"
    printf "     -d                      Generates a development overrides.\\n"
    printf "     -o FILENAME             Output to the given file.\\n"
    printf "\\n"
    printf "CONFIG:\\n"
    printf "\\n"
    printf "     -i IMAGE                Specify an alternative image name.\\n"
    printf "     -n NETWORK              Specify an external network.\\n"
    printf "     -p DB_PASSWORD          Specify a PostgreSQL password.\\n"
    printf "     -s AUTH_SECRET          Specify an AUTH_SECRET variable.\\n"
    printf "     -S SESSION_SECRET       Specify a SESSION_SECRET variable.\\n"
    printf "     -f ENV                  Specify an ENV file to load ENV from.\\n"
    printf "\\n"
}

OPTIND=1

DEV_MODE=0
OUTPUT_FILENAME=""
IMAGE_NAME=""
EXTERNAL_NETWORK=""
DB_PASSWORD=""
AUTH_SECRET=""
SESSION_SECRET=""
ENV_FILE=""

while getopts "hdo:i:n:p:s:S:f:" opt; do
    case "$opt" in
        d ) DEV_MODE=1;;
        o ) OUTPUT_FILENAME=$OPTARG;;
        i ) IMAGE_NAME=$OPTARG;;
        n ) EXTERNAL_NETWORK=$OPTARG;;
        p ) DB_PASSWORD=$OPTARG;;
        s ) AUTH_SECRET=$OPTARG;;
        S ) SESSION_SECRET=$OPTARG;;
        f ) ENV_FILE=$OPTARG;;
        h ) print_usage; exit 2;;
        * ) print_usage; exit 1;;
    esac
done

shift $((OPTIND-1))
if [ "${1:-}" = "--" ]; then
    shift
fi


## Normalizing
##

[ -z "$SESSION_SECRET" ] && SESSION_SECRET=$(openssl rand -hex 32)
[ -z "$AUTH_SECRET" ]    && AUTH_SECRET=$(openssl rand -hex 32)
[ -z "$DB_PASSWORD" ]    && DB_PASSWORD=$(openssl rand -base64 24 | tr '+/' '-_')
[ -z "$IMAGE_NAME" ]     && IMAGE_NAME="sirn/fanboi2:latest"


## Presets
##

YML_PRESETS="$YML_PRESETS
x-presets:
  fanboi2: &fanboi2
    environment:
      AUTH_SECRET: $AUTH_SECRET
      SESSION_SECRET: $SESSION_SECRET
      DATABASE_URL: postgresql://fanboi2:$DB_PASSWORD@postgres:5432/fanboi2\
" # EOF

if [ $DEV_MODE = 0 ]; then
    YML_PRESETS="$YML_PRESETS
    image: $IMAGE_NAME\
" # EOF
else
    YML_PRESETS="$YML_PRESETS
      POSTGRESQL_TEST_DATABASE: postgresql://fanboi2:$DB_PASSWORD@postgres:5432/fanboi2_test
      SERVER_DEV: \"true\"
    image: sirn/fanboi2:dev
    volumes:
      - ./Makefile:/src/Makefile
      - ./alembic.ini:/src/alembic.ini
      - ./fanboi2:/src/fanboi2
      - ./migration:/src/migration
      - ./setup.cfg:/src/setup.cfg
      - ./setup.py:/src/setup.py\
" # EOF
fi

if [ -n "$ENV_FILE" ]; then
    YML_PRESETS="$YML_PRESETS
    env_file:
      - $ENV_FILE\
" # EOF
fi


## Services
##

YML_SERVICES="$YML_SERVICES
  postgres:
    environment:
      DB_PASSWORD: $DB_PASSWORD

  web:
    <<: *fanboi2\
" # EOF

if [ $DEV_MODE = 1 ]; then
    YML_SERVICES="$YML_SERVICES
    build: .
    command: [make, devserve]

  assets:
    image: sirn/fanboi2-assets:dev
    build:
      context: .
      target: assets
    volumes:
      - ./Makefile:/src/Makefile
      - ./assets:/src/assets
      - ./fanboi2/static:/src/fanboi2/static
      - ./gulpfile.js:/src/gulpfile.js
      - ./package.json:/src/package.json
      - ./tsconfig.json:/src/tsconfig.json
      - ./yarn.lock:/src/yarn.lock
    command: [make, devassets]
\
" # EOF
fi

YML_SERVICES="$YML_SERVICES
  worker:
    <<: *fanboi2
    depends_on:
      - web

  beat:
    <<: *fanboi2
    depends_on:
      - web

  migrate:
    <<: *fanboi2
    depends_on:
      - web\
" # EOF


## Network
##

if [ -n "$EXTERNAL_NETWORK" ]; then
    YML_NETWORKS="
  fbnet:
    external:
      name: $EXTERNAL_NETWORK\
" # EOF
fi


## Output
##

print_yaml() {
    printf -- "---\\nversion: \"3.4\"\\n"
    [ -n "$YML_PRESETS" ]  && printf "%s\\n"             "$YML_PRESETS"
    [ -n "$YML_SERVICES" ] && printf "\\nservices:%s\\n" "$YML_SERVICES"
    [ -n "$YML_NETWORKS" ] && printf "\\nnetworks:%s\\n" "$YML_NETWORKS"
}

if [ -n "$OUTPUT_FILENAME" ]; then
    TMPFILE=$(mktemp)
    trap 'rm -f $TMPFILE' 0 1 2 3 6 14 15
    print_yaml | tee "$TMPFILE" >/dev/null
    cp "$TMPFILE" "$OUTPUT_FILENAME"
else
    print_yaml
fi
