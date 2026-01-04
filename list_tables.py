from sqlalchemy import create_engine, inspect
import pandas as pd

sqlite_file = 'test.sqlite'
engine = create_engine(f'sqlite:///{sqlite_file}')
inspector = inspect(engine)
table_names = inspector.get_table_names()

with open('tables.txt', 'w') as f:
    for table in table_names:
        f.write(table + '\n')
