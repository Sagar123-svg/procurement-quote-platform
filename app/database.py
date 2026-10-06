import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite for local development. Later, set DATABASE_URL to a PostgreSQL URL, e.g.
# postgresql+psycopg2://user:password@localhost:5432/procurement
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./procurement.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
