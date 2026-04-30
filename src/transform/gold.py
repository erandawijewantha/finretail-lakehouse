from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from src.utils.db import get_engine
from src.utils.logger import get_logger


logger = get_logger(__name__)


def read_table(schema: str, table_name: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {schema}.{table_name}", engine)


def truncate_gold(table_name: str) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE gold.{table_name}"))


def write_gold(df: pd.DataFrame, table_name: str) -> None:
    engine = get_engine()
    df.to_sql(
        name=table_name,
        con=engine,
        schema="gold",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )


def load_dimensions() -> None:
    mappings = {
        "dim_customer_current": (
            "dim_customer",
            [
                "customer_id",
                "full_name",
                "gender",
                "date_of_birth",
                "city",
                "region",
                "customer_segment",
                "risk_tier",
                "kyc_status",
                "is_active",
            ],
        ),
        "dim_account_current": (
            "dim_account",
            [
                "account_id",
                "customer_id",
                "branch_id",
                "account_type",
                "currency_code",
                "account_status",
                "opened_date",
                "closed_date",
                "current_balance",
            ],
        ),
        "dim_card_current": (
            "dim_card",
            [
                "card_id",
                "customer_id",
                "account_id",
                "card_type",
                "card_status",
                "issued_date",
                "expiry_date",
                "credit_limit",
            ],
        ),
        "dim_merchant_current": (
            "dim_merchant",
            [
                "merchant_id",
                "merchant_name",
                "category_code",
                "city",
                "country_code",
                "merchant_status",
                "risk_level",
            ],
        ),
    }

    for silver_table, (gold_table, cols) in mappings.items():
        df = read_table("silver", silver_table)[cols].copy()
        truncate_gold(gold_table)
        write_gold(df, gold_table)
        logger.info("Loaded %s rows to gold.%s", len(df), gold_table)


def load_fact_card_transactions() -> pd.DataFrame:
    txns = read_table("silver", "card_transactions_clean")

    txns["transaction_ts"] = pd.to_datetime(txns["transaction_ts"], errors="coerce")
    txns["transaction_date"] = txns["transaction_ts"].dt.date

    fact = txns[
        [
            "transaction_id",
            "card_id",
            "customer_id",
            "merchant_id",
            "transaction_date",
            "transaction_ts",
            "transaction_type",
            "transaction_status",
            "amount",
            "currency_code",
            "amount_lkr",
            "channel",
            "is_card_present",
        ]
    ].copy()

    truncate_gold("fact_card_transactions")
    write_gold(fact, "fact_card_transactions")

    logger.info("Loaded %s rows to gold.fact_card_transactions", len(fact))
    return fact


def load_fact_account_transactions() -> pd.DataFrame:
    txns = read_table("silver", "account_transactions_clean")

    txns["transaction_ts"] = pd.to_datetime(txns["transaction_ts"], errors="coerce")
    txns["transaction_date"] = txns["transaction_ts"].dt.date

    fact = txns[
        [
            "account_transaction_id",
            "account_id",
            "customer_id",
            "transaction_date",
            "transaction_ts",
            "transaction_type",
            "debit_credit_flag",
            "amount",
            "currency_code",
            "balance_after",
        ]
    ].copy()

    truncate_gold("fact_account_transactions")
    write_gold(fact, "fact_account_transactions")

    logger.info("Loaded %s rows to gold.fact_account_transactions", len(fact))
    return fact


def load_fact_refunds() -> pd.DataFrame:
    refunds = read_table("silver", "refunds_clean")

    refunds["refund_ts"] = pd.to_datetime(refunds["refund_ts"], errors="coerce")
    refunds["refund_date"] = refunds["refund_ts"].dt.date

    fact = refunds[
        [
            "refund_id",
            "transaction_id",
            "card_id",
            "customer_id",
            "merchant_id",
            "refund_date",
            "refund_ts",
            "refund_amount",
            "refund_reason",
        ]
    ].copy()

    truncate_gold("fact_refunds")
    write_gold(fact, "fact_refunds")

    logger.info("Loaded %s rows to gold.fact_refunds", len(fact))
    return fact


def load_fact_chargebacks() -> pd.DataFrame:
    chargebacks = read_table("silver", "chargebacks_clean")

    chargebacks["opened_at"] = pd.to_datetime(chargebacks["opened_at"], errors="coerce")
    chargebacks["opened_date"] = chargebacks["opened_at"].dt.date

    fact = chargebacks[
        [
            "chargeback_id",
            "transaction_id",
            "customer_id",
            "merchant_id",
            "opened_date",
            "opened_at",
            "resolved_at",
            "dispute_reason",
            "chargeback_amount",
            "dispute_status",
        ]
    ].copy()

    truncate_gold("fact_chargebacks")
    write_gold(fact, "fact_chargebacks")

    logger.info("Loaded %s rows to gold.fact_chargebacks", len(fact))
    return fact


def load_fact_risk_flags() -> pd.DataFrame:
    risk_flags = read_table("silver", "risk_flags_clean")

    risk_flags["flag_ts"] = pd.to_datetime(risk_flags["flag_ts"], errors="coerce")
    risk_flags["flag_date"] = risk_flags["flag_ts"].dt.date

    fact = risk_flags[
        [
            "risk_flag_id",
            "customer_id",
            "transaction_id",
            "flag_date",
            "flag_ts",
            "risk_score",
            "risk_reason",
            "model_version",
            "flag_status",
        ]
    ].copy()

    truncate_gold("fact_risk_flags")
    write_gold(fact, "fact_risk_flags")

    logger.info("Loaded %s rows to gold.fact_risk_flags", len(fact))
    return fact


def build_mart_daily_transaction_summary(fact_card_txns: pd.DataFrame) -> None:
    mart = (
        fact_card_txns.groupby(
            ["transaction_date", "channel", "transaction_status"],
            as_index=False,
        )
        .agg(
            total_transactions=("transaction_id", "nunique"),
            total_amount_lkr=("amount_lkr", "sum"),
            avg_amount_lkr=("amount_lkr", "mean"),
        )
    )

    truncate_gold("mart_daily_transaction_summary")
    write_gold(mart, "mart_daily_transaction_summary")

    logger.info("Loaded %s rows to gold.mart_daily_transaction_summary", len(mart))


def build_mart_merchant_risk_summary(
    fact_card_txns: pd.DataFrame,
    fact_refunds: pd.DataFrame,
    fact_chargebacks: pd.DataFrame,
    fact_risk_flags: pd.DataFrame,
) -> None:
    txn_agg = (
        fact_card_txns.groupby("merchant_id", as_index=False)
        .agg(
            total_transactions=("transaction_id", "nunique"),
            total_amount_lkr=("amount_lkr", "sum"),
        )
    )

    refund_agg = (
        fact_refunds.groupby("merchant_id", as_index=False)
        .agg(
            refund_count=("refund_id", "nunique"),
            refund_amount=("refund_amount", "sum"),
        )
    )

    chargeback_agg = (
        fact_chargebacks.groupby("merchant_id", as_index=False)
        .agg(
            chargeback_count=("chargeback_id", "nunique"),
            chargeback_amount=("chargeback_amount", "sum"),
        )
    )

    risk_txn = fact_risk_flags.merge(
        fact_card_txns[["transaction_id", "merchant_id"]],
        on="transaction_id",
        how="left",
    )

    risk_agg = (
        risk_txn.groupby("merchant_id", as_index=False)
        .agg(avg_risk_score=("risk_score", "mean"))
    )

    mart = (
        txn_agg.merge(refund_agg, on="merchant_id", how="left")
        .merge(chargeback_agg, on="merchant_id", how="left")
        .merge(risk_agg, on="merchant_id", how="left")
    )

    fill_cols = [
        "refund_count",
        "refund_amount",
        "chargeback_count",
        "chargeback_amount",
        "avg_risk_score",
    ]

    for col in fill_cols:
        mart[col] = mart[col].fillna(0)

    truncate_gold("mart_merchant_risk_summary")
    write_gold(mart, "mart_merchant_risk_summary")

    logger.info("Loaded %s rows to gold.mart_merchant_risk_summary", len(mart))


def build_mart_customer_risk_summary(
    fact_card_txns: pd.DataFrame,
    fact_account_txns: pd.DataFrame,
    fact_refunds: pd.DataFrame,
    fact_chargebacks: pd.DataFrame,
    fact_risk_flags: pd.DataFrame,
) -> None:
    card_agg = (
        fact_card_txns.groupby("customer_id", as_index=False)
        .agg(
            total_card_transactions=("transaction_id", "nunique"),
            total_card_amount_lkr=("amount_lkr", "sum"),
        )
    )

    account_agg = (
        fact_account_txns.groupby("customer_id", as_index=False)
        .agg(total_account_transactions=("account_transaction_id", "nunique"))
    )

    refund_agg = (
        fact_refunds.groupby("customer_id", as_index=False)
        .agg(refund_count=("refund_id", "nunique"))
    )

    chargeback_agg = (
        fact_chargebacks.groupby("customer_id", as_index=False)
        .agg(chargeback_count=("chargeback_id", "nunique"))
    )

    risk_agg = (
        fact_risk_flags.groupby("customer_id", as_index=False)
        .agg(
            risk_flag_count=("risk_flag_id", "nunique"),
            avg_risk_score=("risk_score", "mean"),
        )
    )

    mart = (
        card_agg.merge(account_agg, on="customer_id", how="left")
        .merge(refund_agg, on="customer_id", how="left")
        .merge(chargeback_agg, on="customer_id", how="left")
        .merge(risk_agg, on="customer_id", how="left")
    )

    for col in [
        "total_account_transactions",
        "refund_count",
        "chargeback_count",
        "risk_flag_count",
        "avg_risk_score",
    ]:
        mart[col] = mart[col].fillna(0)

    truncate_gold("mart_customer_risk_summary")
    write_gold(mart, "mart_customer_risk_summary")

    logger.info("Loaded %s rows to gold.mart_customer_risk_summary", len(mart))


def main() -> None:
    load_dimensions()

    fact_card_txns = load_fact_card_transactions()
    fact_account_txns = load_fact_account_transactions()
    fact_refunds = load_fact_refunds()
    fact_chargebacks = load_fact_chargebacks()
    fact_risk_flags = load_fact_risk_flags()

    build_mart_daily_transaction_summary(fact_card_txns)
    build_mart_merchant_risk_summary(
        fact_card_txns=fact_card_txns,
        fact_refunds=fact_refunds,
        fact_chargebacks=fact_chargebacks,
        fact_risk_flags=fact_risk_flags,
    )
    build_mart_customer_risk_summary(
        fact_card_txns=fact_card_txns,
        fact_account_txns=fact_account_txns,
        fact_refunds=fact_refunds,
        fact_chargebacks=fact_chargebacks,
        fact_risk_flags=fact_risk_flags,
    )


if __name__ == "__main__":
    main()