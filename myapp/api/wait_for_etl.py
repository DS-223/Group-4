import docker
import time
import sys
from sqlalchemy import create_engine, inspect, text
import os
from database.engine import engine
from database.database import Base

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

# Ensure all tables from models are created
Base.metadata.create_all(bind=engine)

# All tables are now required
REQUIRED_TABLES = [
    'users',
    'locations',
    'property_types',
    'properties',
    'images',
    'property_ml_ready',
    'predictions'
]

def wait_for_etl(container_name='etl', timeout=600):
    print("Waiting for ETL container to finish...")
    elapsed = 0
    while elapsed < timeout:
        try:
            container = client.containers.get(container_name)
            status = container.status
            if status == 'exited':
                exit_code = container.attrs['State']['ExitCode']
                if exit_code == 0:
                    print("ETL finished successfully.")
                    break
                else:
                    print(f"ETL failed with exit code {exit_code}. Exiting.")
                    sys.exit(1)
            else:
                print(f"ETL status: {status}. Waiting...")
        except docker.errors.NotFound:
            print("ETL container not found. Retrying...")
        time.sleep(5)
        elapsed += 5
    else:
        print("Timeout waiting for ETL to finish.")
        sys.exit(1)

    check_database_tables()

def check_database_tables():
    print("Verifying tables in database...")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("DATABASE_URL not set in environment.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    existing_tables = inspector.get_table_names()
    missing = [t for t in REQUIRED_TABLES if t not in existing_tables]
    if missing:
        print(f"Missing required tables: {missing}")
        sys.exit(1)

    with engine.connect() as conn:
        for table in REQUIRED_TABLES:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            if count == 0:
                print(f"Table '{table}' is empty.")
                sys.exit(1)
            else:
                print(f"Table '{table}' has {count} rows.")

    print("All required tables exist and have data.")

if __name__ == "__main__":
    wait_for_etl()
