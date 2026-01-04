from sqlalchemy import create_engine, inspect

sqlite_file = 'test.sqlite'
engine = create_engine(f'sqlite:///{sqlite_file}')
inspector = inspect(engine)

tables = inspector.get_table_names()
print(f"Tables found: {tables}")

if 'aggregated_transaction_state' in tables:
    cols = [c['name'] for c in inspector.get_columns('aggregated_transaction_state')]
    print(f"aggregated_transaction_state columns: {cols}")

if 'top_transaction_district' in tables:
    print("top_transaction_district exists")
else:
    print("top_transaction_district DOES NOT exist")
