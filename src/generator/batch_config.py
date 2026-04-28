from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


LOCAL_GENERATED_DIR = Path("data/generated")


@dataclass(frozen=True)
class BatchConfig:
    batch_id: str = "001"
    batch_date: date = date(2026, 1, 1)

    n_customers: int = 10_000
    n_accounts: int = 15_000
    n_cards: int = 12_000
    n_merchants: int = 2_000
    n_card_transactions: int = 100_000
    n_account_transactions: int = 80_000
    n_login_events: int = 50_000
    n_device_events: int = 30_000
    n_risk_flags: int = 5_000