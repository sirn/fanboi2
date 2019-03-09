#!/bin/sh

set -e

if [ -z "$DB_PASSWORD" ]; then
    printf "DB_PASSWORD is not present, exiting.\\n"
    exit 1
fi

psql -v ON_ERROR_STOP=1 --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" <<EOF
CREATE USER fanboi2 WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
CREATE DATABASE fanboi2 WITH OWNER fanboi2;
CREATE DATABASE fanboi2_test WITH OWNER fanboi2;
GRANT ALL PRIVILEGES ON DATABASE fanboi2 TO fanboi2;
GRANT ALL PRIVILEGES ON DATABASE fanboi2_test TO fanboi2;
EOF
