from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()


def get_mysql_url() -> str:
    """Build the MySQL connection URL from settings."""
    return (
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"
    )


# Single, authoritative engine — MySQL only. If MySQL is unreachable the app
# fails fast at import time (desired: no silent fallback to a different store).
engine = create_engine(
    get_mysql_url(),
    pool_pre_ping=True,   # detect dropped connections before use
    pool_recycle=3600,    # recycle connections hourly (avoids MySQL wait_timeout)
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_tables():
    """Create all tables on the MySQL database if they don't yet exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
