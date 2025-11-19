import sqlite3

conn = sqlite3.connect('wedcraft.db')
cursor = conn.cursor()

print('=== ALL TABLES IN DATABASE ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f'Table: {table[0]}')

print('\n=== TABLE SCHEMAS ===')
for table in tables:
    table_name = table[0]
    print(f'\n--- {table_name} ---')
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()