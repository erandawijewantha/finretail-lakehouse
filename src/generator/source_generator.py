from __future__ import annotations

from datetime import datetime, time, timedelta
import json
import random
from pathlib import Path

import pandas as pd
from faker import Faker

from src.generator.batch_config import BatchConfig, LOCAL_GENERATED_DIR
from src.generator.ids import make_id
from src.utils.logger import get_logger


logger = get_logger(__name__)
fake = Faker()


def batch_day_window(batch: BatchConfig) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(batch.batch_date, time.min)
    end_dt = datetime.combine(batch.batch_date + timedelta(days=1), time.min)
    return start_dt, end_dt


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    df.to_csv(path, index=False)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    df.to_parquet(path, index=False)


def write_json_lines(records: list[dict], path: Path) -> None:
    ensure_dir(path.parent)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, default=str) + "\n")


def output_path(source_system: str, entity_name: str, batch: BatchConfig, extension: str) -> Path:
    return (
        LOCAL_GENERATED_DIR
        / "raw"
        / source_system
        / entity_name
        / f"dt={batch.batch_date.isoformat()}"
        / f"{entity_name}_{batch.batch_id}.{extension}"
    )


def generate_branches(batch: BatchConfig) -> pd.DataFrame:
    regions = ["WESTERN", "CENTRAL", "SOUTHERN", "NORTHERN", "EASTERN"]
    branch_types = ["MAIN", "MINI", "DIGITAL_SERVICE"]

    rows = []

    for i in range(1, 101):
        created_at = fake.date_time_between(start_date="-5y", end_date="-1y")

        rows.append(
            {
                "branch_id": make_id("BR", i, 5),
                "branch_name": f"{fake.city()} Branch",
                "city": fake.city(),
                "region": random.choice(regions),
                "branch_type": random.choice(branch_types),
                "is_active": random.choice([True, True, True, False]),
                "created_at": created_at,
                "updated_at": created_at + timedelta(days=random.randint(0, 500)),
            }
        )

    return pd.DataFrame(rows)


def generate_customers(batch: BatchConfig) -> pd.DataFrame:
    segments = ["MASS", "AFFLUENT", "SME_OWNER", "SALARIED", "STUDENT"]
    risk_tiers = ["LOW", "MEDIUM", "HIGH"]
    kyc_statuses = ["VERIFIED", "PENDING", "REJECTED"]

    rows = []

    for i in range(1, batch.n_customers + 1):
        created_at = fake.date_time_between(start_date="-4y", end_date="-30d")

        rows.append(
            {
                "customer_id": make_id("CUS", i, 8),
                "full_name": fake.name(),
                "gender": random.choice(["MALE", "FEMALE"]),
                "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=75),
                "email": fake.email() if random.random() > 0.03 else None,
                "phone": fake.phone_number() if random.random() > 0.05 else None,
                "city": fake.city(),
                "region": random.choice(
                    ["WESTERN", "CENTRAL", "SOUTHERN", "NORTHERN", "EASTERN"]
                ),
                "customer_segment": random.choice(segments),
                "risk_tier": random.choice(risk_tiers),
                "kyc_status": random.choice(kyc_statuses),
                "is_active": random.choice([True, True, True, False]),
                "created_at": created_at,
                "updated_at": created_at + timedelta(days=random.randint(0, 300)),
            }
        )

    return pd.DataFrame(rows)


def generate_accounts(
    batch: BatchConfig,
    customers: pd.DataFrame,
    branches: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    customer_ids = customers["customer_id"].tolist()
    branch_ids = branches["branch_id"].tolist()

    for i in range(1, batch.n_accounts + 1):
        created_at = fake.date_time_between(start_date="-4y", end_date="-20d")
        account_status = random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "DORMANT", "CLOSED"])

        rows.append(
            {
                "account_id": make_id("ACC", i, 8),
                "customer_id": random.choice(customer_ids),
                "branch_id": random.choice(branch_ids),
                "account_type": random.choice(["SAVINGS", "CURRENT", "SALARY", "LOAN"]),
                "currency_code": random.choice(["LKR", "USD", "EUR", "GBP"]),
                "account_status": account_status,
                "opened_date": created_at.date(),
                "closed_date": (
                    fake.date_between(start_date="-1y", end_date="today")
                    if account_status == "CLOSED"
                    else None
                ),
                "current_balance": round(random.uniform(-50_000, 5_000_000), 2),
                "created_at": created_at,
                "updated_at": created_at + timedelta(days=random.randint(0, 300)),
            }
        )

    return pd.DataFrame(rows)


def generate_cards(batch: BatchConfig, accounts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    account_rows = accounts[["account_id", "customer_id"]].to_dict("records")

    for i in range(1, batch.n_cards + 1):
        account = random.choice(account_rows)
        issued_date = fake.date_between(start_date="-4y", end_date="-30d")

        rows.append(
            {
                "card_id": make_id("CARD", i, 8),
                "customer_id": account["customer_id"],
                "account_id": account["account_id"],
                "card_type": random.choice(["DEBIT", "CREDIT", "PREPAID"]),
                "card_status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "BLOCKED", "EXPIRED"]),
                "issued_date": issued_date,
                "expiry_date": issued_date + timedelta(days=365 * 4),
                "credit_limit": round(random.uniform(25_000, 1_000_000), 2),
                "created_at": issued_date,
                "updated_at": issued_date + timedelta(days=random.randint(0, 800)),
            }
        )

    return pd.DataFrame(rows)


def generate_merchants(batch: BatchConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    categories = [
        ("GROCERY", "Grocery Stores", False),
        ("FUEL", "Fuel Stations", False),
        ("ECOM", "E-Commerce", False),
        ("TRAVEL", "Travel", False),
        ("GAMING", "Gaming", True),
        ("CRYPTO", "Crypto Services", True),
    ]

    merchant_categories = pd.DataFrame(
        [
            {
                "category_code": code,
                "category_name": name,
                "high_risk_category": high_risk,
                "created_at": fake.date_time_between(start_date="-5y", end_date="-1y"),
                "updated_at": fake.date_time_between(start_date="-1y", end_date="now"),
            }
            for code, name, high_risk in categories
        ]
    )

    rows = []
    category_codes = merchant_categories["category_code"].tolist()

    for i in range(1, batch.n_merchants + 1):
        onboarded_at = fake.date_time_between(start_date="-5y", end_date="-30d")

        rows.append(
            {
                "merchant_id": make_id("MER", i, 7),
                "merchant_name": fake.company(),
                "category_code": random.choice(category_codes),
                "city": fake.city(),
                "country_code": random.choice(["LK", "IN", "SG", "US", "GB"]),
                "merchant_status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "SUSPENDED"]),
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "onboarded_at": onboarded_at,
                "updated_at": onboarded_at + timedelta(days=random.randint(0, 900)),
            }
        )

    return pd.DataFrame(rows), merchant_categories


def generate_exchange_rates(batch: BatchConfig) -> pd.DataFrame:
    rows = []
    currencies = {"LKR": 1.0, "USD": 300.0, "EUR": 325.0, "GBP": 380.0}

    for currency, base_rate in currencies.items():
        rows.append(
            {
                "currency_code": currency,
                "rate_date": batch.batch_date,
                "rate_to_lkr": round(base_rate * random.uniform(0.98, 1.02), 6),
                "created_at": datetime.combine(batch.batch_date, time.min),
            }
        )

    return pd.DataFrame(rows)


def generate_card_transactions(
    batch: BatchConfig,
    cards: pd.DataFrame,
    merchants: pd.DataFrame,
    exchange_rates: pd.DataFrame,
) -> pd.DataFrame:
    start_dt, end_dt = batch_day_window(batch)

    rows = []
    card_rows = cards[["card_id", "customer_id"]].to_dict("records")
    merchant_ids = merchants["merchant_id"].tolist()
    rate_map = dict(zip(exchange_rates["currency_code"], exchange_rates["rate_to_lkr"]))

    for i in range(1, batch.n_card_transactions + 1):
        card = random.choice(card_rows)
        currency = random.choice(["LKR", "LKR", "LKR", "USD", "EUR"])
        amount = round(random.uniform(100, 250_000), 2)
        ts = fake.date_time_between(start_date=start_dt, end_date=end_dt)

        rows.append(
            {
                "transaction_id": make_id("TXN", i, 10),
                "card_id": card["card_id"],
                "customer_id": card["customer_id"],
                "merchant_id": random.choice(merchant_ids),
                "transaction_ts": ts,
                "transaction_type": random.choice(
                    ["PURCHASE", "PURCHASE", "PURCHASE", "AUTH_ONLY", "REVERSAL"]
                ),
                "transaction_status": random.choice(
                    ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "PENDING"]
                ),
                "amount": amount,
                "currency_code": currency,
                "amount_lkr": round(amount * float(rate_map[currency]), 2),
                "channel": random.choice(["POS", "ECOM", "ATM", "MOBILE"]),
                "auth_code": fake.bothify(text="AUTH####??"),
                "is_card_present": random.choice([True, False]),
                "created_at": ts,
            }
        )

    df = pd.DataFrame(rows)

    duplicates = df.sample(frac=0.01, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)

    return df


def generate_account_transactions(batch: BatchConfig, accounts: pd.DataFrame) -> pd.DataFrame:
    start_dt, end_dt = batch_day_window(batch)

    rows = []
    account_rows = accounts[["account_id", "customer_id", "currency_code"]].to_dict("records")

    for i in range(1, batch.n_account_transactions + 1):
        account = random.choice(account_rows)
        amount = round(random.uniform(100, 500_000), 2)
        ts = fake.date_time_between(start_date=start_dt, end_date=end_dt)

        rows.append(
            {
                "account_transaction_id": make_id("ATX", i, 10),
                "account_id": account["account_id"],
                "customer_id": account["customer_id"],
                "transaction_ts": ts,
                "transaction_type": random.choice(["CASH", "TRANSFER", "FEE", "INTEREST", "REVERSAL"]),
                "debit_credit_flag": random.choice(["DR", "CR"]),
                "amount": amount,
                "currency_code": account["currency_code"],
                "balance_after": round(random.uniform(-50_000, 5_000_000), 2),
                "description": fake.sentence(nb_words=6),
                "created_at": ts,
            }
        )

    return pd.DataFrame(rows)


def generate_refunds(batch: BatchConfig, card_transactions: pd.DataFrame) -> pd.DataFrame:
    success_txns = card_transactions[
        card_transactions["transaction_status"] == "SUCCESS"
    ].drop_duplicates("transaction_id")

    sample = success_txns.sample(frac=0.015, random_state=42)
    rows = []

    for i, (_, txn) in enumerate(sample.iterrows(), start=1):
        refund_ts = pd.to_datetime(txn["transaction_ts"]) + timedelta(days=random.randint(1, 5))

        rows.append(
            {
                "refund_id": make_id("REF", i, 8),
                "transaction_id": txn["transaction_id"],
                "card_id": txn["card_id"],
                "customer_id": txn["customer_id"],
                "merchant_id": txn["merchant_id"],
                "refund_ts": refund_ts,
                "refund_amount": round(float(txn["amount"]) * random.choice([0.25, 0.5, 1.0]), 2),
                "refund_reason": random.choice(
                    ["CUSTOMER_RETURN", "DUPLICATE_CHARGE", "MERCHANT_ERROR", "FRAUD_CLAIM"]
                ),
                "created_at": refund_ts,
            }
        )

    return pd.DataFrame(rows)


def generate_chargebacks(batch: BatchConfig, card_transactions: pd.DataFrame) -> pd.DataFrame:
    success_txns = card_transactions[
        card_transactions["transaction_status"] == "SUCCESS"
    ].drop_duplicates("transaction_id")

    sample = success_txns.sample(frac=0.005, random_state=7)
    rows = []

    for i, (_, txn) in enumerate(sample.iterrows(), start=1):
        opened_at = pd.to_datetime(txn["transaction_ts"]) + timedelta(days=random.randint(3, 20))

        rows.append(
            {
                "chargeback_id": make_id("CBK", i, 8),
                "transaction_id": txn["transaction_id"],
                "customer_id": txn["customer_id"],
                "merchant_id": txn["merchant_id"],
                "dispute_reason": random.choice(["FRAUD", "NOT_RECEIVED", "DUPLICATE", "QUALITY_ISSUE"]),
                "chargeback_amount": txn["amount"],
                "dispute_status": random.choice(["OPEN", "UNDER_REVIEW", "WON", "LOST"]),
                "opened_at": opened_at,
                "resolved_at": (
                    opened_at + timedelta(days=random.randint(5, 45))
                    if random.random() > 0.5
                    else None
                ),
                "updated_at": opened_at + timedelta(days=random.randint(0, 45)),
            }
        )

    return pd.DataFrame(rows)


def generate_login_events(batch: BatchConfig, customers: pd.DataFrame) -> list[dict]:
    start_dt, end_dt = batch_day_window(batch)

    customer_ids = customers["customer_id"].tolist()
    rows = []

    for i in range(1, batch.n_login_events + 1):
        login_ts = fake.date_time_between(start_date=start_dt, end_date=end_dt)

        rows.append(
            {
                "login_event_id": make_id("LOG", i, 10),
                "customer_id": random.choice(customer_ids),
                "device_id": make_id("DEV", random.randint(1, 20_000), 8),
                "login_ts": login_ts.isoformat(),
                "channel": random.choice(["MOBILE_APP", "WEB", "API"]),
                "ip_address": fake.ipv4_public(),
                "country_code": random.choice(["LK", "LK", "LK", "IN", "SG", "US"]),
                "login_status": random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"]),
                "failure_reason": random.choice([None, "BAD_PASSWORD", "LOCKED", "OTP_FAILED"]),
                "event_payload": {
                    "browser": random.choice(["Chrome", "Edge", "Safari", "Firefox"]),
                    "schema_version": random.choice(["1.0", "1.1"]),
                },
            }
        )

    return rows


def generate_device_events(batch: BatchConfig, customers: pd.DataFrame) -> list[dict]:
    start_dt, end_dt = batch_day_window(batch)

    customer_ids = customers["customer_id"].tolist()
    rows = []

    for i in range(1, batch.n_device_events + 1):
        event_ts = fake.date_time_between(start_date=start_dt, end_date=end_dt)

        rows.append(
            {
                "device_event_id": make_id("DVE", i, 10),
                "customer_id": random.choice(customer_ids),
                "device_id": make_id("DEV", random.randint(1, 20_000), 8),
                "event_ts": event_ts.isoformat(),
                "event_type": random.choice(["REGISTERED", "TRUSTED", "REMOVED", "APP_UPDATED"]),
                "os_name": random.choice(["Android", "iOS", "Windows"]),
                "app_version": random.choice(["1.0.0", "1.1.0", "2.0.0"]),
                "ip_address": fake.ipv4_public(),
                "country_code": random.choice(["LK", "LK", "LK", "IN", "SG", "US"]),
                "event_payload": {
                    "rooted_device": random.choice([True, False, False]),
                    "schema_version": random.choice(["1.0", "1.1", "2.0"]),
                },
            }
        )

    return rows


def generate_risk_flags(batch: BatchConfig, card_transactions: pd.DataFrame) -> list[dict]:
    unique_txns = card_transactions.drop_duplicates("transaction_id")

    sample_size = min(batch.n_risk_flags, len(unique_txns))
    txns = unique_txns.sample(n=sample_size, random_state=42)

    rows = []

    for i, (_, txn) in enumerate(txns.iterrows(), start=1):
        risk_score = round(random.uniform(0.01, 0.99), 4)

        rows.append(
            {
                "risk_flag_id": make_id("RSK", i, 10),
                "customer_id": txn["customer_id"],
                "transaction_id": txn["transaction_id"],
                "flag_ts": pd.to_datetime(txn["transaction_ts"]).isoformat(),
                "risk_score": risk_score,
                "risk_reason": random.choice(
                    ["HIGH_AMOUNT", "FOREIGN_IP", "HIGH_RISK_MERCHANT", "VELOCITY"]
                ),
                "model_version": random.choice(["v1.0", "v1.1"]),
                "flag_status": random.choice(["OPEN", "REVIEWED", "DISMISSED"]),
                "event_payload": {
                    "threshold": 0.75,
                    "rule_triggered": risk_score >= 0.75,
                },
            }
        )

    return rows


def generate_batch(batch: BatchConfig) -> None:
    random.seed(42)
    Faker.seed(42)

    logger.info("Generating FinRetail batch %s for %s", batch.batch_id, batch.batch_date)

    branches = generate_branches(batch)
    customers = generate_customers(batch)
    accounts = generate_accounts(batch, customers, branches)
    cards = generate_cards(batch, accounts)
    merchants, merchant_categories = generate_merchants(batch)
    exchange_rates = generate_exchange_rates(batch)

    card_transactions = generate_card_transactions(batch, cards, merchants, exchange_rates)
    account_transactions = generate_account_transactions(batch, accounts)
    refunds = generate_refunds(batch, card_transactions)
    chargebacks = generate_chargebacks(batch, card_transactions)
    login_events = generate_login_events(batch, customers)
    device_events = generate_device_events(batch, customers)
    risk_flags = generate_risk_flags(batch, card_transactions)

    write_parquet(branches, output_path("core_banking", "branches", batch, "parquet"))
    write_parquet(customers, output_path("core_banking", "customers", batch, "parquet"))
    write_parquet(accounts, output_path("core_banking", "accounts", batch, "parquet"))
    write_parquet(account_transactions, output_path("core_banking", "account_transactions", batch, "parquet"))

    write_csv(cards, output_path("card_processor", "cards", batch, "csv"))
    write_csv(card_transactions, output_path("card_processor", "card_transactions", batch, "csv"))
    write_csv(refunds, output_path("card_processor", "refunds", batch, "csv"))
    write_csv(chargebacks, output_path("card_processor", "chargebacks", batch, "csv"))

    write_parquet(merchants, output_path("merchant_system", "merchants", batch, "parquet"))
    write_parquet(
        merchant_categories,
        output_path("merchant_system", "merchant_categories", batch, "parquet"),
    )

    write_csv(exchange_rates, output_path("reference_data", "exchange_rates", batch, "csv"))

    write_json_lines(login_events, output_path("digital_channels", "login_events", batch, "json"))
    write_json_lines(device_events, output_path("digital_channels", "device_events", batch, "json"))
    write_json_lines(risk_flags, output_path("risk_engine", "risk_flags", batch, "json"))

    logger.info("Batch generation complete.")


def main() -> None:
    generate_batch(BatchConfig())


if __name__ == "__main__":
    main()