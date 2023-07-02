#!/bin/bash

set -e

# Define the PostgreSQL host and port
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Wait for PostgreSQL to be ready
/wait-for-it.sh -t 60 ${POSTGRES_HOST}:${POSTGRES_PORT} -- echo "PostgreSQL is up."

# Run the command provided as an argument
exec "$@"