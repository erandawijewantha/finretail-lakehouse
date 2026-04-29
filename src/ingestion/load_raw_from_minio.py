from __future__ import annotations

import io
import json 
import pandas as pd

from sqlalchemy import text

from src.config.settings import settings
from src.storage.minio_client import get_s3_client
from src.utils.db import get_engine
from src.utils.logger import get_logger


logger = get_logger(__name__)


def read_file(client, object_key: str) -> pd.DataFrame:
    obj = client.get_object(Bucket=settings.minio_bucket, Key=object_key)
    data = obj["Body"].read()
    
    if object_key.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data))
    
    elif object_key.endswith(".parquet"):
        return pd.read_parquet(io.BytesIO(data))
    
    elif object_key.endswith(".json"):
        return pd.read_json(io.BytesIO(data), lines=True)
    
    else:
        raise ValueError(f"Unsupported file type: {object_key}")
    
def get_pending_files():
    engine = get_engine()
    
    query = """
    SELECT *
    FROM control.file_registry
    WHERE status = 'LANDED'
    """
    
    return pd.read_sql(query, engine)

def prepare_json_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "event_payload" in result.columns:
        result["event_payload"] = result["event_payload"].apply(
            lambda x: json.dumps(x) if isinstance(x, dict) else x
        )

    return result

def load_file(row):
    client = get_s3_client()
    engine = get_engine()
    
    object_key = row["object_key"]
    entity_name = row["entity_name"]
    
    df = read_file(client, object_key)
    
    df = prepare_json_columns(df)
    
    # add metadata
    df["source_system"] = row["source_system"]
    df["object_key"] = object_key
    df["file_checksum"] = row["file_checksum"]
    df["landed_at"] = row["landed_at"]
    
    df.to_sql(
        name=entity_name,
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    
    update_sql = """
    UPDATE control.file_registry
    SET status = 'PROCESSED', processed_at = CURRENT_TIMESTAMP
    WHERE object_key = :object_key
    """
    
    with engine.begin() as conn:
        conn.execute(text(update_sql), {"object_key": object_key})
        
    logger.info("Loaded %s rows into %s", len(df), entity_name)
    
def main():
    files = get_pending_files()
    
    if files.empty:
        logger.info("No files to process")
        return

    for _, row in files.iterrows():
        load_file(row)
        
if __name__ == "__main__":
    main()
    