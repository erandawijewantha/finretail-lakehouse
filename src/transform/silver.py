from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from src.quality.silver_rules import (
    filter_valid_account_transactions,
    filter_valid_card_transactions,
    filter_valid_chargebacks,
    filter_valid_device_events,
    filter_valid_login_events,
    filter_valid_refunds,
    filter_valid_risk_flags,
)
from src.utils.db import get_engine
from src.utils.logger import get_logger


logger = get_logger(__name__)


def read_bronze(table_name: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM bronze.{table_name}", engine)


def truncate_silver(table_name: str) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE silver.{table_name}"))


def write_silver(df: pd.DataFrame, table_name: str) -> None:
    engine = get_engine()

    df.to_sql(
        name=table_name,
        con=engine,
        schema="silver",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )


def load_current_dimensions() -> None:
    dimension_map = {
        "customers": "dim_customer_current",
        "accounts": "dim_account_current",
        "cards": "dim_card_current",
        "merchants": "dim_merchant_current",
    }

    for bronze_table, silver_table in dimension_map.items():
        df = read_bronze(bronze_table)
        truncate_silver(silver_table)
        write_silver(df, silver_table)
        logger.info("Loaded %s rows to silver.%s", len(df), silver_table)


def load_clean_transactions() -> None:
    customers = read_bronze("customers")
    accounts = read_bronze("accounts")
    cards = read_bronze("cards")
    merchants = read_bronze("merchants")

    card_txns = read_bronze("card_transactions")
    account_txns = read_bronze("account_transactions")
    refunds = read_bronze("refunds")
    chargebacks = read_bronze("chargebacks")
    login_events = read_bronze("login_events")
    device_events = read_bronze("device_events")
    risk_flags = read_bronze("risk_flags")

    card_txns_clean = filter_valid_card_transactions(
        txns=card_txns,
        cards=cards,
        customers=customers,
        merchants=merchants,
    )

    account_txns_clean = filter_valid_account_transactions(
        txns=account_txns,
        accounts=accounts,
        customers=customers,
    )

    refunds_clean = filter_valid_refunds(
        refunds=refunds,
        card_transactions=card_txns_clean,
    )

    chargebacks_clean = filter_valid_chargebacks(
        chargebacks=chargebacks,
        card_transactions=card_txns_clean,
    )

    login_events_clean = filter_valid_login_events(
        login_events=login_events,
        customers=customers,
    )

    device_events_clean = filter_valid_device_events(
        device_events=device_events,
        customers=customers,
    )

    risk_flags_clean = filter_valid_risk_flags(
        risk_flags=risk_flags,
        customers=customers,
        card_transactions=card_txns_clean,
    )

    outputs = {
        "card_transactions_clean": card_txns_clean,
        "account_transactions_clean": account_txns_clean,
        "refunds_clean": refunds_clean,
        "chargebacks_clean": chargebacks_clean,
        "login_events_clean": login_events_clean,
        "device_events_clean": device_events_clean,
        "risk_flags_clean": risk_flags_clean,
    }

    for table_name, df in outputs.items():
        truncate_silver(table_name)
        write_silver(df, table_name)
        logger.info("Loaded %s rows to silver.%s", len(df), table_name)


def main() -> None:
    load_current_dimensions()
    load_clean_transactions()


if __name__ == "__main__":
    main()