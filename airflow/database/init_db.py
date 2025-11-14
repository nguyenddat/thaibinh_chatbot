import os
from dotenv import load_dotenv
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from airflow.models import Variable

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()