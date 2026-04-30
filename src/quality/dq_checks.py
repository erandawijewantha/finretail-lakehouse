from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text

from src.utils.db import get_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DQResult:
    layer_name: str
    table_name: str
    check_name: str
    check_status: str
    failed_count: int
    details: str


def run_count_query(sql: str) -> int:
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


def insert_dq_result(result: DQResult) -> None:
    engine = get_engine()

    sql = text("""
        INSERT INTO audit.data_quality_result (
            layer_name,
            table_name,
            check_name,
            check_status,
            failed_count,
            details
        )
        VALUES (
            :layer_name,
            :table_name,
            :check_name,
            :check_status,
            :failed_count,
            :details
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            sql,
            {
                "layer_name": result.layer_name,
                "table_name": result.table_name,
                "check_name": result.check_name,
                "check_status": result.check_status,
                "failed_count": result.failed_count,
                "details": result.details,
            },
        )


def evaluate_check(
    layer_name: str,
    table_name: str,
    check_name: str,
    sql: str,
    details: str,
) -> DQResult:
    failed_count = run_count_query(sql)
    status = "PASS" if failed_count == 0 else "FAIL"

    result = DQResult(
        layer_name=layer_name,
        table_name=table_name,
        check_name=check_name,
        check_status=status,
        failed_count=failed_count,
        details=details,
    )

    insert_dq_result(result)

    logger.info(
        "DQ %s | %s.%s | failed_count=%s",
        status,
        layer_name,
        table_name,
        failed_count,
    )

    return result


def run_dq_checks() -> None:
    checks = [
        {
            "layer_name": "silver",
            "table_name": "card_transactions_clean",
            "check_name": "transaction_id_not_null",
            "sql": """
                SELECT COUNT(*)
                FROM silver.card_transactions_clean
                WHERE transaction_id IS NULL
            """,
            "details": "Card transactions must have transaction_id.",
        },
        {
            "layer_name": "silver",
            "table_name": "card_transactions_clean",
            "check_name": "no_duplicate_transaction_id",
            "sql": """
                SELECT COUNT(*)
                FROM (
                    SELECT transaction_id
                    FROM silver.card_transactions_clean
                    GROUP BY transaction_id
                    HAVING COUNT(*) > 1
                ) x
            """,
            "details": "Transaction IDs must be unique.",
        },
        {
            "layer_name": "silver",
            "table_name": "card_transactions_clean",
            "check_name": "no_orphan_customer",
            "sql": """
                SELECT COUNT(*)
                FROM silver.card_transactions_clean t
                LEFT JOIN silver.dim_customer_current c
                    ON t.customer_id = c.customer_id
                WHERE c.customer_id IS NULL
            """,
            "details": "Every card transaction must map to a valid customer.",
        },
        {
            "layer_name": "silver",
            "table_name": "card_transactions_clean",
            "check_name": "no_orphan_card",
            "sql": """
                SELECT COUNT(*)
                FROM silver.card_transactions_clean t
                LEFT JOIN silver.dim_card_current c
                    ON t.card_id = c.card_id
                WHERE c.card_id IS NULL
            """,
            "details": "Every card transaction must map to a valid card.",
        },
        {
            "layer_name": "silver",
            "table_name": "card_transactions_clean",
            "check_name": "amount_non_negative",
            "sql": """
                SELECT COUNT(*)
                FROM silver.card_transactions_clean
                WHERE amount < 0 OR amount_lkr < 0
            """,
            "details": "Transaction amount and LKR amount must be non-negative.",
        },
        {
            "layer_name": "silver",
            "table_name": "refunds_clean",
            "check_name": "refund_transaction_exists",
            "sql": """
                SELECT COUNT(*)
                FROM silver.refunds_clean r
                LEFT JOIN silver.card_transactions_clean t
                    ON r.transaction_id = t.transaction_id
                WHERE t.transaction_id IS NULL
            """,
            "details": "Every refund must map to a valid card transaction.",
        },
        {
            "layer_name": "silver",
            "table_name": "chargebacks_clean",
            "check_name": "chargeback_transaction_exists",
            "sql": """
                SELECT COUNT(*)
                FROM silver.chargebacks_clean c
                LEFT JOIN silver.card_transactions_clean t
                    ON c.transaction_id = t.transaction_id
                WHERE t.transaction_id IS NULL
            """,
            "details": "Every chargeback must map to a valid card transaction.",
        },
        {
            "layer_name": "gold",
            "table_name": "fact_card_transactions",
            "check_name": "fact_row_count_matches_silver",
            "sql": """
                SELECT ABS(
                    (SELECT COUNT(*) FROM gold.fact_card_transactions)
                    -
                    (SELECT COUNT(*) FROM silver.card_transactions_clean)
                )
            """,
            "details": "Gold fact card transaction count should match silver clean transaction count.",
        },
        {
            "layer_name": "gold",
            "table_name": "mart_merchant_risk_summary",
            "check_name": "merchant_mart_not_empty",
            "sql": """
                SELECT CASE
                    WHEN (SELECT COUNT(*) FROM gold.mart_merchant_risk_summary) = 0
                    THEN 1 ELSE 0
                END
            """,
            "details": "Merchant risk mart should not be empty.",
        },
    ]

    failed_checks = []

    for check in checks:
        result = evaluate_check(**check)
        if result.check_status == "FAIL":
            failed_checks.append(result)

    if failed_checks:
        raise RuntimeError(f"{len(failed_checks)} data quality checks failed.")

    logger.info("All data quality checks passed.")


if __name__ == "__main__":
    run_dq_checks()