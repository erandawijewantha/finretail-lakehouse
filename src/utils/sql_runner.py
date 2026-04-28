from __future__ import annotations

from pathlib import Path 

from src.utils.db import execute_sql
from src.utils.logger import get_logger

logger = get_logger(__name__)

def read_sql_file(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    
    return file_path.read_text(encoding="utf-8")

def execute_sql_file(file_path: Path) -> None:
    sql = read_sql_file(file_path)
    execute_sql(sql)
    logger.info("Executed SQL file: %s", file_path)
    