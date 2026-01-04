from sqlalchemy import create_engine, inspect
import pandas as pd

sqlite_file = 'test.sqlite'
engine = create_engine(f'sqlite:///{sqlite_file}')
inspector = inspect(engine)

table_names = inspector.get_table_names()

print(f"Found {len(table_names)} tables:")
for table_name in table_names:
    print(f"\nTable: {table_name}")
    columns = inspector.get_columns(table_name)
    for column in columns:
        print(f"  - {column['name']} ({column['type']})")
