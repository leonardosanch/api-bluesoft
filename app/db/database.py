from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from app.schemas import Cliente
from app.db.models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bluesoft"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
         db.close()