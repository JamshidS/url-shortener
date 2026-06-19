from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Optional: fallback to hardcoded PostgreSQL (e.g. for local dev)
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:12345@localhost:5432/test"
    print("Warning: DATABASE_URL not found in .env. Using hardcoded PostgreSQL URL.")



Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
