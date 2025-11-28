"""
Convert New Inspections File.txt to Excel with duplicates removed
"""
import re
import pandas as pd
from collections import OrderedDict

# Read the file
with open('New Inspections File.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Parse the data
data = []
for line in lines:
    # Skip header lines, empty lines, and separator lines
    if line.startswith('=') or line.startswith('-') or line.startswith('#') or not line.strip():
        continue
    if 'INSPECTIONS FOR' in line or 'Report Generated' in line or 'Total Inspections' in line or 'Date Range' in line:
        continue
    if 'Remote ID' in line and 'Client Name' in line:
        continue

    # Parse data line using regex for fixed-width format
    # Format: #  Remote ID  Client Name  Inspection Date  Account Code  Commodity
    match = re.match(r'\s*(\d+)\s+(\d+)\s+(.+?)\s{2,}(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(\S+)\s*$', line)
    if match:
        row_num, remote_id, client_name, insp_date, account_code, commodity = match.groups()
        data.append({
            'Remote ID': int(remote_id),
            'Client Name': client_name.strip(),
            'Inspection Date': insp_date,
            'Account Code': account_code,
            'Commodity': commodity
        })

print(f"Total rows parsed: {len(data)}")

# Create DataFrame
df = pd.DataFrame(data)

# Remove duplicates based on Account Code (keeping first occurrence)
df_unique = df.drop_duplicates(subset=['Account Code'], keep='first')

print(f"Rows after removing duplicates: {len(df_unique)}")
print(f"Duplicates removed: {len(data) - len(df_unique)}")

# Sort by Inspection Date (newest first) then by Remote ID
df_unique = df_unique.sort_values(['Inspection Date', 'Remote ID'], ascending=[False, True])

# Reset index
df_unique = df_unique.reset_index(drop=True)

# Export to Excel
output_file = 'New_Inspections_By_Account.xlsx'
df_unique.to_excel(output_file, index=False, engine='openpyxl')

print(f"\nExported to: {output_file}")
print(f"\nSummary by Client Name:")
print(df_unique.groupby('Client Name').size().sort_values(ascending=False).head(20))

print(f"\nSummary by Commodity:")
print(df_unique.groupby('Commodity').size().sort_values(ascending=False))
