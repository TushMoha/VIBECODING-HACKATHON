# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use SQLite database stored locally in a file
DATABASE_URL = "sqlite:///chatbot.db"

# Create the engine (connects to DB)
engine = create_engine(DATABASE_URL, echo=True)

# Base class for all models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
