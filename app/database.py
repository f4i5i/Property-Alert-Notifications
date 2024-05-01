from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the path to the SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()