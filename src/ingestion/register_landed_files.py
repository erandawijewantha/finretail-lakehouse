from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import engine 
from sqlalchemy import text

from src.config.settings import settings 
from src.storage.minio_client import get_s3_client
from src.utils.db import get_engine
from src.utils.hashing import hash_string 
from src.utils.logger import get_logger 

logger = get_logger(__name__)

def parse_object_key(object_key: str) -> tuple[str, str]:
    """
    raw/source_system/entity_name/dt=YYYY-MM-DD/file.ext
    """
    parts = object_key.split("/")
    
    source_system = parts[1]
    entity_name = parts[2]
    
    return source_system, entity_name 

def register_files() -> None:
    client = get_s3_client()
    engine = get_engine()
    
    response = client.list_objects_v2(Bucket=settings.minio_bucket)
    
    if "Contents" not in response:
        logger.warning("No objects found in MinIO bucket")
        return 
    
    rows = []
    
    for obj in response["Contents"]:
        object_key = obj["Key"]
        file_size = obj["Size"]
        
        source_system, entity_name = parse_object_key(object_key)
        
        file_checksum = hash_string(object_key) # simple first version
        
        rows.append(
            {
                "source_system": source_system,
                "entity_name": entity_name,
                "object_key": object_key,
                "file_checksum": file_checksum,
                "file_size_bytes": file_size,
                "row_count": None,
                "landed_at": datetime.now(),
                "status": "LANDED",
            }
        )
    insert_sql = """
    INSERT INTO control.file_registry (
        source_system,
        entity_name,
        object_key,
        file_checksum,
        file_size_bytes,
        row_count,
        landed_at,
        status
    )
    VALUES (
        :source_system,
        :entity_name,
        :object_key,
        :file_checksum,
        :file_size_bytes,
        :row_count,
        :landed_at,
        :status
    )
    ON CONFLICT (object_key, file_checksum) DO NOTHING
    """
    
    with engine.begin() as conn:
        conn.execute(text(insert_sql), rows)
        
    logger.info("Registered %s files into control.file_registry", len(rows))
    
if __name__ == "__main__":
    register_files()
        
    