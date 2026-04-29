from __future__ import annotations

BUSINESS_KEYS = {
    "customers": ["customer_id"],
    "accounts": ["account_id"],
    "branches": ["branch_id"],
    "cards": ["card_id"],
    "merchants": ["merchant_id"],
    "merchant_categories": ["category_code"],
    "exchange_rates": ["currency_code", "rate_date"],
    "card_transactions": ["transaction_id"],
    "account_transactions": ["account_transaction_id"],
    "refunds": ["refund_id"],
    "chargebacks": ["chargeback_id"],
    "login_events": ["login_event_id"],
    "device_events": ["device_event_id"],
    "risk_flags": ["risk_flag_id"],
}

LATEST_BY_UPDATED_AT = {
    "customers",
    "accounts",
    "branches",
    "cards",
    "merchants",
    "merchant_categories",
    "chargebacks",
    "risk_flags",
}

APPEND_DEDUP = {
    "exchange_rates",
    "card_transactions",
    "account_transactions",
    "refunds",
    "login_events",
    "device_events",
}