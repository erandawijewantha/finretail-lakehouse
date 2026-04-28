from __future__ import annotations

from pathlib import Path

from src.generator.batch_config import LOCAL_GENERATED_DIR
from src.storage.minio_client import ensure_bucket_exists, upload_file
from src.utils.logger import get_logger


logger = get_logger(__name__)


def local_to_object_key(file_path: Path) -> str:
    relative_path = file_path.relative_to(LOCAL_GENERATED_DIR)
    return relative_path.as_posix()


def land_generated_files_to_minio() -> None:
    ensure_bucket_exists()

    files = [
        *LOCAL_GENERATED_DIR.rglob("*.csv"),
        *LOCAL_GENERATED_DIR.rglob("*.json"),
        *LOCAL_GENERATED_DIR.rglob("*.parquet"),
    ]

    if not files:
        logger.warning("No generated files found under %s", LOCAL_GENERATED_DIR)
        return

    for file_path in files:
        object_key = local_to_object_key(file_path)
        upload_file(file_path, object_key)

    logger.info("Uploaded %s files to MinIO.", len(files))


def main() -> None:
    land_generated_files_to_minio()


if __name__ == "__main__":
    main()