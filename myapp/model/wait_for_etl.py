"""
This script ensures the readiness of the PostgreSQL database for machine learning operations
by waiting for the ETL (Extract-Transform-Load) Docker container to complete successfully
and verifying that all required tables are present and populated.

Functionality:
- Connects to Docker and monitors the status of the ETL container.
- Waits for the ETL job to finish (with a timeout) and handles errors if the job fails.
- After ETL completion, connects to the PostgreSQL database using SQLAlchemy.
- Checks for the presence and non-emptiness of required tables (`users`, `locations`, etc.).
- Optionally checks for tables like `predictions` and logs their status.
- Creates tables using SQLAlchemy's metadata if they do not exist.

Usage:
    Run this script as a startup check before model training:
    $ python etl_monitor.py

Environment:
- Requires the Docker daemon to be running.
- Expects a valid `DATABASE_URL` in environment variables for PostgreSQL connection.

"""

import docker
import time
import sys
import os
from sqlalchemy import create_engine, inspect, text
from database.engine import engine
from database.database import Base
from loguru import logger


# Docker client to monitor ETL container
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

# Create database tables if not exist
Base.metadata.create_all(bind=engine)

REQUIRED_TABLES = ['users', 'locations', 'property_types', 'properties', 'images', 'property_ml_ready']
OPTIONAL_TABLES = ['predictions']

def wait_for_etl(container_name='etl', timeout=600):
    """
    Waits for the ETL Docker container to finish its job within the timeout.
    Exits the script if ETL fails or times out.
    """
    logger.info("Waiting for ETL container to finish...")
    elapsed = 0
    while elapsed < timeout:
        try:
            container = client.containers.get(container_name)
            status = container.status
            if status == 'exited':
                exit_code = container.attrs['State']['ExitCode']
                if exit_code == 0:
                    logger.info("ETL finished successfully.")
                    break
                else:
                    logger.error(f"ETL failed with exit code {exit_code}. Exiting.")
                    sys.exit(1)
            else:
                logger.info(f"ETL status: {status}. Waiting...")
        except docker.errors.NotFound:
            logger.warning("ETL container not found. Retrying...")
        time.sleep(5)
        elapsed += 5
    else:
        logger.error("Timeout waiting for ETL to finish.")
        sys.exit(1)

    check_database_tables()

def check_database_tables():
    """
    Validates that all required tables exist and are populated.
    Logs the status and exits on failure.
    """
    logger.info("Verifying tables in database...")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set in environment.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    existing_tables = inspector.get_table_names()
    missing = [t for t in REQUIRED_TABLES if t not in existing_tables]
    if missing:
        logger.error(f"Missing required tables: {missing}")
        sys.exit(1)

    with engine.connect() as conn:
        for table in REQUIRED_TABLES:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            if count == 0:
                logger.error(f"Table '{table}' is empty.")
                sys.exit(1)
            else:
                logger.info(f"Table '{table}' has {count} rows.")

        for table in OPTIONAL_TABLES:
            if table in existing_tables:
                logger.info(f"Optional table '{table}' found (may be empty).")
            else:
                logger.info(f"Optional table '{table}' not found (will be created by model).")

    logger.info("All required tables exist and have data.")

if __name__ == "__main__":
    wait_for_etl()
