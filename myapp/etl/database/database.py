import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from dotenv import load_dotenv
import os

def get_db():
    """
    Function to get a database session.
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