from __future__ import annotations

from pathlib import Path

from src.utils.sql_runner import execute_sql_file


DDL_DIR = Path("sql/ddl")


def main() -> None:
    ddl_files = [
        DDL_DIR / "001_create_schemas.sql",
        DDL_DIR / "002_create_control_tables.sql",
        DDL_DIR / "003_create_raw_tables.sql",
    ]

    for ddl_file in ddl_files:
        execute_sql_file(ddl_file)


if __name__ == "__main__":
    main()