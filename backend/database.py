from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, SSL_ROOT_CERT, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT
from pathlib import Path

# Create database engine with SSL parameters
connect_args = {}
if Path(SSL_ROOT_CERT).exists():
    connect_args = {
        "sslmode": "verify-full",
        "sslrootcert": SSL_ROOT_CERT
    }
else:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    echo=False,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import models to register them with Base
    from models import patient
    Base.metadata.create_all(bind=engine)
