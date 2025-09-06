# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# PostgreSQL database URL - Use environment variable for production
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for database URL, fallback to local development
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:admin123@database-1.ccda62qsu988.us-east-1.rds.amazonaws.com:5432/postgres"
)


# Create engine
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
        # connect_args not needed for PostgreSQL
    )
    # Test the connection immediately
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Database connection successful! ✅")
except OperationalError as e:
    print(f"Database connection failed: {e} ❌")
    print("Please check your DATABASE_URL and ensure the database is running and accessible.")
    # Depending on your application structure, you might want to exit or handle this error more gracefully.
    # For example, if this is a FastAPI app, you might not want to start if DB is down.
    # exit(1)


# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()