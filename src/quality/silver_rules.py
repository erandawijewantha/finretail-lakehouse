from __future__ import annotations

import json

import pandas as pd

VALID_TRANSACTION_STATUS = {"SUCCESS", "FAILED", "PENDING"}
VALID_TRANSACTION_TYPE = {"PURCHASE", "AUTH_ONLY", "REVERSAL"}
VALID_CHANNELS = {"POS", "ECOM", "ATM", "MOBILE"}

VALID_ACCOUNT_TXN_TYPES = {"CASH", "TRANSFER", "FEE", "INTEREST", "REVERSAL"}
VALID_DR_CR = {"DR", "CR"}

VALID_LOGIN_STATUS = {"SUCCESS", "FAILED"}
VALID_DEVICE_EVENT_TYPES = {"REGISTERED", "TRUSTED", "REMOVED", "APP_UPDATED"}
VALID_RISK_FLAG_STATUS = {"OPEN", "REVIEWED", "DISMISSED"}

def clean_code(series: pd.Series) -> pd.Series:
    if series is None:
        return series
    
    return (
        series.astype("string")
        .str.strip()
        .str.strip('"')
        .str.strip("'")
        .str.upper()
    )
    
def prepare_json_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    
    if "event_payload" in result.columns:
        result["event_payload"] = result["event_payload"].apply(
            lambda x: json.dumps(x) if isinstance(x, dict) else x
        )                              
    return result 

def prepare_card_transactions(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    
    for col in ["transaction_status", "transaction_type", "channel", "currency_code"]:
        if col in result.columns:
            result[col] = clean_code(result[col])
            
    for col in ["transaction_ts", "created_at", "landed_at"]:
        if col in result.columns:
            result[col]=pd.to_datetime(result[col], errors="coerce")
            
    for col in ["amount", "amount_lkr"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors = "coerce")
    
    return result

def prepare_account_transactions(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    
    for col in ["transaction_type", "debit_credit_flag", "currency_code"]:
        if col in result.columns:
            result[col] = clean_code(result[col])
            
    for col in ["transaction_ts", "created_at", "landed_at"]:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce")
            
    for col in ["amount","balance_after"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")
            
    return result

def filter_valid_card_transactions(
    txns: pd.DataFrame,
    cards: pd.DataFrame,
    customers: pd.DataFrame,
    merchants: pd.DataFrame,
) -> pd.DataFrame:
    result = prepare_card_transactions(txns)
    
    result = result[result["transaction_id"].notna()]
    result = result[result["card_id"].isin(set(cards["card_id"].dropna()))]
    result = result[result["customer_id"].isin(set(customers["customer_id"].dropna()))]
    result = result[result["merchant_id"].isin(set(merchants["merchant_id"].dropna()))]
    result = result[result["transaction_status"].isin(VALID_TRANSACTION_STATUS)]
    result = result[result["transaction_type"].isin(VALID_TRANSACTION_TYPE)]
    result = result[result["channel"].isin(VALID_CHANNELS)]
    result = result[result["amount"].fillna(0) >= 0]
    result = result[result["amount_lkr"].fillna(0) >= 0]
    
    return result

def filter_valid_account_transactions(
    txns: pd.DataFrame,
    accounts: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    result = prepare_account_transactions(txns)
    
    result = result[result["account_transaction_id"].notna()]
    result = result[result["account_id"].isin(set(accounts["account_id"].dropna()))]
    result = result[result["customer_id"].isin(set(customers["customer_id"].dropna()))]
    result = result[result["transaction_type"].isin(VALID_ACCOUNT_TXN_TYPES)]
    result = result[result["debit_credit_flag"].isin(VALID_DR_CR)]
    result = result[result["amount"].fillna(0) >= 0]

    return result
    
def filter_valid_refunds(
    refunds: pd.DataFrame,
    card_transactions: pd.DataFrame,
) -> pd.DataFrame:
    result = refunds.copy()

    result["refund_ts"] = pd.to_datetime(result["refund_ts"], errors="coerce")
    result["refund_amount"] = pd.to_numeric(result["refund_amount"], errors="coerce")

    valid_txn_ids = set(card_transactions["transaction_id"].dropna())

    result = result[result["refund_id"].notna()]
    result = result[result["transaction_id"].isin(valid_txn_ids)]
    result = result[result["refund_amount"].fillna(0) >= 0]

    return result


def filter_valid_chargebacks(
    chargebacks: pd.DataFrame,
    card_transactions: pd.DataFrame,
) -> pd.DataFrame:
    result = chargebacks.copy()

    result["chargeback_amount"] = pd.to_numeric(result["chargeback_amount"], errors="coerce")
    result["dispute_status"] = clean_code(result["dispute_status"])

    valid_txn_ids = set(card_transactions["transaction_id"].dropna())

    result = result[result["chargeback_id"].notna()]
    result = result[result["transaction_id"].isin(valid_txn_ids)]
    result = result[result["chargeback_amount"].fillna(0) >= 0]

    return result


def filter_valid_login_events(
    login_events: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    result = login_events.copy()

    result["login_status"] = clean_code(result["login_status"])
    result["login_ts"] = pd.to_datetime(result["login_ts"], errors="coerce")

    result = result[result["login_event_id"].notna()]
    result = result[result["customer_id"].isin(set(customers["customer_id"].dropna()))]
    result = result[result["login_status"].isin(VALID_LOGIN_STATUS)]

    return prepare_json_columns(result)


def filter_valid_device_events(
    device_events: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    result = device_events.copy()

    result["event_type"] = clean_code(result["event_type"])
    result["event_ts"] = pd.to_datetime(result["event_ts"], errors="coerce")

    result = result[result["device_event_id"].notna()]
    result = result[result["customer_id"].isin(set(customers["customer_id"].dropna()))]
    result = result[result["event_type"].isin(VALID_DEVICE_EVENT_TYPES)]

    return prepare_json_columns(result)


def filter_valid_risk_flags(
    risk_flags: pd.DataFrame,
    customers: pd.DataFrame,
    card_transactions: pd.DataFrame,
) -> pd.DataFrame:
    result = risk_flags.copy()

    result["flag_status"] = clean_code(result["flag_status"])
    result["flag_ts"] = pd.to_datetime(result["flag_ts"], errors="coerce")
    result["risk_score"] = pd.to_numeric(result["risk_score"], errors="coerce")

    result = result[result["risk_flag_id"].notna()]
    result = result[result["customer_id"].isin(set(customers["customer_id"].dropna()))]
    result = result[result["transaction_id"].isin(set(card_transactions["transaction_id"].dropna()))]
    result = result[result["flag_status"].isin(VALID_RISK_FLAG_STATUS)]
    result = result[result["risk_score"].between(0, 1)]

    return prepare_json_columns(result)

