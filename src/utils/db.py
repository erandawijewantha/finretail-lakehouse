from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_engine() -> Engine:
    return create_engine(
        settings.sqlalchemy_url,
        echo=settings.postgres_echo,
        future=True,
        pool_pre_ping=True,
    )
    
def test_connection() -> None:
    engine = get_engine()
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS health_check"))
        row = result.fetchone()
        
    logger.info("PostgreSQL connection successful: %s", row.health_check)
    
def execute_sql(sql: str) -> None:
    engine = get_engine()
    
    with engine.begin() as conn:
        conn.execute(text(sql))
        