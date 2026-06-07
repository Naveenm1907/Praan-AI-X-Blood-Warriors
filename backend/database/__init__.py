"""Database package for PRAAN AI - engine, session, models"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT

# SSL is already embedded in DATABASE_URL by config.py (sslmode= param).
# Passing SSL settings again via connect_args would cause psycopg2 conflicts,
# so we use an empty dict here.
engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    echo=False,
    connect_args={},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import models to register them with Base
    from models import patient, task, workflow
    from models import patient  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Re-export models for convenience
from database.models import Patient, MedicalReport, Donor, TransfusionRequest

__all__ = [
    'engine', 'SessionLocal', 'Base', 'get_db', 'init_db',
    'Patient', 'MedicalReport', 'Donor', 'TransfusionRequest',
]
