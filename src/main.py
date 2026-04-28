from __future__ import annotations

from src.storage.minio_client import ensure_bucket_exists, list_objects
from src.utils.db import test_connection


def main() -> None:
    test_connection()
    ensure_bucket_exists()

    objects = list_objects()
    print("Current MinIO objects:", objects)


if __name__ == "__main__":
    main()