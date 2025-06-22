import logging
import os

import redis
from sqlmodel import create_engine

POSTGRES_DB = os.getenv("POSTGRES_DB", "backend_database")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construct DATABASE_URL using .format()
DATABASE_URL = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)
DEBUG = os.getenv("DEBUG", "False") == "True"


# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=DEBUG)

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)

logger = logging.getLogger("uvicorn")
