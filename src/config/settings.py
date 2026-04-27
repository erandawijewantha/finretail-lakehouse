from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv 

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR/".env"

load_dotenv(ENV_PATH)

def _get_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

@dataclass(frozen=True)
class Settings:
    app_env: str
    
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_echo: bool

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_secure: bool
    
    @property
    def sqlalchemy_url(self) -> str:
        return (
                f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        
def get_settings() -> Settings:
    return Settings (
        app_env = os.getenv("APP_ENV", "dev"),
        
        postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_db=os.getenv("POSTGRES_DB", "finretail"),
        postgres_user=os.getenv("POSTGRES_USER", "postgres"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        postgres_echo=_get_bool(os.getenv("POSTGRES_ECHO"), default=False),

        minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        minio_bucket=os.getenv("MINIO_BUCKET", "finretail-lakehouse"),
        minio_secure=_get_bool(os.getenv("MINIO_SECURE"), default=False),
    )
    
settings = get_settings()
