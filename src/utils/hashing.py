from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def hash_file(file_path: Path) -> str:
    hasher = hashlib.sha256()
    
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
            
    return hasher.hexdigest()

def build_row_hash(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    safe_df = df[columns].fillna("").astype(str)
    return safe_df.agg("||".join, axis=1).apply(hash_string)


