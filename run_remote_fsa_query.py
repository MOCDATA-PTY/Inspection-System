#!/usr/bin/env python3
"""
Attempt to run the FSA_INSPECTION_QUERY against the remote SQL Server and print sample rows.

Usage:
    python run_remote_fsa_query.py --limit 20

Note: This requires `pymssql` to be installed and network access to the configured server.
"""

import os
import sys
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from main.views.data_views import FSA_INSPECTION_QUERY, SQLSERVER_CONFIG, SQLSERVER_CONNECTION_STRING


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', '-n', type=int, default=20, help='Number of rows to fetch and show')
    args = parser.parse_args()

    try:
        import pymssql
    except Exception as e:
        print("pymssql module not available. Install it with: pip install pymssql")
        print(f"Import error: {e}")
        sys.exit(2)

    # Use connection values from module if available; fallback to parts of SQLSERVER_CONFIG
    server = None
    port = None
    user = None
    password = None
    database = None

    try:
        # Try reading a connection string if present
        if SQLSERVER_CONFIG and isinstance(SQLSERVER_CONFIG, dict):
            server = SQLSERVER_CONFIG.get('HOST')
            port = SQLSERVER_CONFIG.get('PORT')
            user = SQLSERVER_CONFIG.get('USER')
            password = SQLSERVER_CONFIG.get('PASSWORD')
            database = SQLSERVER_CONFIG.get('NAME')
    except Exception:
        pass

    # If any are missing, try parsing the SQLSERVER_CONNECTION_STRING
    if not (server and user and database):
        try:
            conn = SQLSERVER_CONNECTION_STRING
            # crude parse for SERVER, DATABASE, UID, PWD
            for part in conn.split(';'):
                if part.upper().startswith('SERVER='):
                    server = part.split('=', 1)[1]
                if part.upper().startswith('DATABASE='):
                    database = part.split('=', 1)[1]
                if part.upper().startswith('UID='):
                    user = part.split('=', 1)[1]
                if part.upper().startswith('PWD='):
                    password = part.split('=', 1)[1]
        except Exception:
            pass

    if not server or not user or not database:
        print("Missing SQL Server connection info. Check `main.views.data_views` for credentials.")
        sys.exit(2)

    print(f"Connecting to SQL Server: server={server} database={database} user={user}")

    # pymssql expects server and port combined as server:port or server,port depending on version
    server_arg = server
    if port:
        server_arg = f"{server},{port}"

    try:
        conn = pymssql.connect(server=server_arg, user=user, password=password, database=database, login_timeout=10)
        cur = conn.cursor()
        print("Connected. Executing query (fetching up to {0} rows)...".format(args.limit))
        cur.execute(FSA_INSPECTION_QUERY)
        cols = [c[0] for c in cur.description] if cur.description else []
        rows = cur.fetchmany(args.limit)
        print(f"Columns: {cols}")
        print(f"Fetched rows: {len(rows)}")
        for r in rows:
            print(r)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting or executing query: {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()
