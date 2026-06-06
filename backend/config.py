import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve backend directory (where this file lives)
BASE_DIR = Path(__file__).resolve().parent

# Load .env from backend directory
load_dotenv(BASE_DIR / ".env")

APP_MODE = os.getenv("APP_MODE", "mock")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "praan")

# SSL Certificate - use the downloaded global-bundle.pem
SSL_ROOT_CERT = str(BASE_DIR / "global-bundle.pem")

# RDS PostgreSQL Configuration
DB_HOST = os.getenv("DB_HOST", "praan-db.cjc6s24mcwn4.eu-north-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Naveenkusu")

# Build DATABASE_URL with SSL
if Path(SSL_ROOT_CERT).exists():
    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?sslmode=verify-full&sslrootcert={SSL_ROOT_CERT}"
    )
else:
    # Fallback: require-ca but no local cert file
    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?sslmode=require"
    )

# Database connection pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
