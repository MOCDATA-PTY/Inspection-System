#!/usr/bin/env python
"""Pull 10 sample rows from each SQL Server table to see what data is available"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pymssql
from django.conf import settings
from datetime import datetime

print("=" * 80)
print("SQL SERVER TABLE SAMPLES - October 2025 onwards")
print("=" * 80)

# Connect to SQL Server
sql_config = settings.DATABASES.get('sql_server', {})
try:
    conn = pymssql.connect(
        server=sql_config.get('HOST'),
        port=int(sql_config.get('PORT', 1433)),
        user=sql_config.get('USER'),
        password=sql_config.get('PASSWORD'),
        database=sql_config.get('NAME'),
        timeout=10
    )
    print("\n[OK] Connected to SQL Server")
    cursor = conn.cursor()
except Exception as e:
    print(f"\n[ERROR] Failed to connect: {e}")
    exit(1)

# Define tables to query - just get ALL columns to see what's available
tables = [
    {
        'name': 'PMPInspectionRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 3  # Just 3 rows to see structure
    },
    {
        'name': 'PMPInspectedProductRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 10
    },
    {
        'name': 'PoultryGradingInspectionRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 3
    },
    {
        'name': 'PoultryLabelInspectionChecklistRecords',
        'columns': '*',
        'date_filter': None,
        'limit': 3
    },
    {
        'name': 'PoultryQuidInspectionRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 3
    },
    {
        'name': 'PoultryInspectionRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 3
    },
    {
        'name': 'RawRMPInspectionRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 3
    },
    {
        'name': 'RawRMPInspectedProductRecordTypes',
        'columns': '*',
        'date_filter': None,
        'limit': 10
    }
]

# Query each table
for table_info in tables:
    table_name = table_info['name']
    columns_spec = table_info['columns']
    date_filter = table_info['date_filter']
    limit = table_info.get('limit', 10)

    print(f"\n{'=' * 80}")
    print(f"TABLE: {table_name}")
    print(f"{'=' * 80}")

    try:
        # Build query
        query = f"SELECT TOP {limit} {columns_spec} FROM {table_name}"
        if date_filter:
            query += f" WHERE {date_filter}"
        query += " ORDER BY Id DESC"  # Get most recent first

        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Print just the first few most important columns (not all 50+ columns)
            max_cols_to_show = 6
            shown_cols = column_names[:max_cols_to_show]

            # Print header
            header = ' | '.join(f"{col:25s}" for col in shown_cols)
            print(header)
            print('-' * len(header))

            # Print rows
            for row in rows:
                # Only show first few columns
                row_values = row[:max_cols_to_show]
                row_str = ' | '.join(f"{str(val)[:25]:25s}" if val is not None else f"{'NULL':25s}" for val in row_values)
                print(row_str)

            print(f"\nFound {len(rows)} rows with {len(column_names)} columns total")
            print(f"Columns: {', '.join(column_names[:15])}{'...' if len(column_names) > 15 else ''}")
        else:
            print("No data found")

    except Exception as e:
        print(f"[ERROR] Error querying {table_name}: {e}")

# Close connection
cursor.close()
conn.close()
print(f"\n{'=' * 80}")
print("Done!")
print(f"{'=' * 80}")
