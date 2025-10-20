#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "getpass",
#     "psycopg2>=2.9.11",
# ]
# ///

"""Script to create the PostgreSQL database and user for TimeTracker."""
# Evan Young October 2025

from getpass import getpass

import psycopg2
from psycopg2 import sql

DB_NAME = 'timetracker_db'
DB_USER = 'timetracker_user'
DB_PASS = 'your_password'


def main() -> None:
    """Create the database, user, and grant privileges."""
    try:
        # Prompt for the Postgres superuser password
        superuser_password = getpass.getpass('Postgres superuser password: ')

        # Connect to the default 'postgres' database as superuser
        conn = psycopg2.connect(dbname='postgres', user='postgres', password=superuser_password)
        conn.autocommit = True
        cur = conn.cursor()

        # Create database if it doesn't exist
        cur.execute('SELECT 1 FROM pg_database WHERE datname=%s;', (DB_NAME,))
        if not cur.fetchone():
            print(f'Creating database {DB_NAME}...')
            cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DB_NAME)))
        else:
            print(f'Database {DB_NAME} already exists.')

        # Create user if it doesn't exist
        cur.execute('SELECT 1 FROM pg_roles WHERE rolname=%s;', (DB_USER,))
        if not cur.fetchone():
            print(f'Creating user {DB_USER}...')
            cur.execute(
                sql.SQL('CREATE USER {} WITH ENCRYPTED PASSWORD %s;').format(sql.Identifier(DB_USER)), (DB_PASS,)
            )
        else:
            print(f'User {DB_USER} already exists.')

        # Grant privileges
        print(f'Granting privileges on {DB_NAME} to {DB_USER}...')
        cur.execute(
            sql.SQL('GRANT ALL PRIVILEGES ON DATABASE {} TO {};').format(
                sql.Identifier(DB_NAME), sql.Identifier(DB_USER)
            )
        )

        print('Setup complete.')

    except Exception as e:
        print(f'Error: {e}')
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
