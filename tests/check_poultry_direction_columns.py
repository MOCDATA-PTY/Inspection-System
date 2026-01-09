"""Check what columns are in the Poultry direction tables"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

sql_server_config = settings.DATABASES.get('sql_server', {})

connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)

print("Checking PoultryDirectionRecordTypes columns...")
cursor.execute("SELECT TOP 1 * FROM AFS.dbo.PoultryDirectionRecordTypes")
result = cursor.fetchone()
if result:
    print(f"Columns: {list(result.keys())}")

connection.close()
