#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$do\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
            CREATE ROLE airflow WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';
            ALTER ROLE airflow CREATEDB;
        ELSE
            RAISE NOTICE 'Role "airflow" already exists. Skipping role creation.';
        END IF;
    EXCEPTION
        WHEN others THEN
            -- Do nothing, role already exists
    END
    \$do\$;

    DO
    \$do\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow') THEN
            CREATE DATABASE airflow;
            GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
        ELSE
            RAISE NOTICE 'Database "airflow" already exists. Skipping database creation.';
        END IF;
    EXCEPTION
        WHEN others THEN
            -- Do nothing, database already exists
    END
    \$do\$;
EOSQL