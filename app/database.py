from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the PostgreSQL database URL
# Format: "postgresql://user:password@host:port/dbname"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Archit%402002@localhost:5432/mydatabase"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Archit%402002@localhost:5432/comm"
# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class to generate new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models to inherit from
Base = declarative_base()


def get_db():
    """
    SQLAlchemy dependency to get a database session.

    Yields a session from the SessionLocal factory and ensures it is
    properly closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()