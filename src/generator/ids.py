from __future__ import annotations


def make_id(prefix: str, number: int, width: int = 8) -> str:
    return f"{prefix}{number:0{width}d}"