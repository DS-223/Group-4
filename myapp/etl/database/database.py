"""
Database Configuration Module.

This module sets up the SQLAlchemy database engine, session factory,
and base declarative class for ORM models. It also provides a utility
function to get a scoped database session.

Uses:
    - SQLAlchemy for ORM.
    - dotenv for environment variable management.

Environment:
    Expects a `.env` file with a key `DATABASE_URL`.
"""

import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from dotenv import load_dotenv
import os

def get_db():
    """
    Function to get a database session.

    Yields:
        Session: SQLAlchemy session instance.

    Ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


load_dotenv(".env")

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = sql.create_engine(DATABASE_URL)

Base = declarative.declarative_base()

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)