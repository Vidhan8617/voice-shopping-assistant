"""
Database engine + session management.

Uses SQLAlchemy's declarative ORM. SQLite by default (zero setup, file-based)
but database_url can point to Postgres in production without changing any
model or query code — that's the point of using an ORM here.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# check_same_thread=False is only needed for SQLite (FastAPI uses multiple
# threads for sync routes); it's a no-op / ignored for other DBs.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session per request and always closes
    it, even if the request raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
