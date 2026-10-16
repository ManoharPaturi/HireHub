# Shared application settings. Environment variables and backend/.env supply
# local credentials, while the defaults describe a local MySQL installation.
# All routers and database helpers reuse the Settings instance at the bottom.

import os
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings


# Pydantic loads typed settings and lets environment configuration override defaults.
class Settings(BaseSettings):
    PROJECT_NAME: str = "HireHub — Internship Portal"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # MySQL connection parameters (the project uses MySQL exclusively — no SQLite fallback).
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "internship_portal")

    # Read .env relative to this file, so settings do not depend on the shell directory.
    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
