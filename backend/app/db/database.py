# MySQL connection setup shared by every route. The engine manages reusable
# connections; a session tracks pending reads/writes for one request. Routers
# explicitly commit changes, and get_db closes the session when a request ends.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()


# Combine settings into the SQLAlchemy connection string; PyMySQL is the driver.
def get_mysql_url() -> str:
    """Build the MySQL connection URL from settings."""
    return (
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"
    )


# Configure the MySQL engine here. Connections are opened when first used;
# startup table creation fails if MySQL is unavailable. No SQLite fallback exists.
engine = create_engine(
    get_mysql_url(),
    pool_pre_ping=True,   # detect dropped connections before use
    pool_recycle=3600,    # recycle connections hourly (avoids MySQL wait_timeout)
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create missing tables from registered models. create_all does not migrate
# columns in a table that already exists.
def init_tables():
    """Create all tables on the MySQL database if they don't yet exist."""
    Base.metadata.create_all(bind=engine)


# FastAPI dependency: open a session for the request, yield it to the route,
# and always close it afterward. Closing does not commit pending changes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
