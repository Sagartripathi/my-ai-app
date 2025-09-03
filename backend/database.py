# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL database URL
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/AI_CHATBOT"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@db:5432/AI_CHATBOT"


# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # connect_args not needed for PostgreSQL
)

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