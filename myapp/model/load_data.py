import pandas as pd
import time
from loguru import logger
from sqlalchemy import inspect
from database.engine import engine
from database.database import Base
from sqlalchemy import text

from database.data_generate import generate_user, generate_location, generate_property, generate_image, generate_property_type

# Create all tables
Base.metadata.create_all(bind=engine)

# List of required tables to check
required_tables = [
    "users",
    "property_types",
    "locations",
    "properties",
    "images",
    "property_ml_ready"
]

# Function to check if a table exists and is non-empty
def is_table_populated(table_name):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        logger.warning(f"Table '{table_name}' does not exist yet.")
        return False
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    logger.info(f"Table '{table_name}' has {result} rows.")
    return result > 0

# Wait until all required tables are populated
def wait_for_tables(timeout_seconds=600, poll_interval=10):
    logger.info("Waiting for ETL to populate required tables...")
    total_waited = 0
    while total_waited < timeout_seconds:
        if all(is_table_populated(table) for table in required_tables):
            logger.success("All required tables are populated.")
            return True
        time.sleep(poll_interval)
        total_waited += poll_interval
        logger.info(f"Checked again after {total_waited} seconds...")
    logger.error("Timeout while waiting for tables to be populated.")
    return False

# Main logic
if wait_for_tables():
    df = pd.read_sql("SELECT * FROM property_ml_ready", engine)
    logger.success(f"Loaded {len(df)} rows from 'property_ml_ready'")
    print(df.head())
else:
    logger.error("ETL did not populate required tables in time. Exiting.")

