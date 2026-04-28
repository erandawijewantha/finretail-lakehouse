CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id VARCHAR(50),
    full_name VARCHAR(200),
    gender VARCHAR(20),
    date_of_birth DATE,
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    region VARCHAR(100),
    customer_segment VARCHAR(50),
    risk_tier VARCHAR(50),
    kyc_status VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.accounts (
    account_id VARCHAR(50),
    customer_id VARCHAR(50),
    branch_id VARCHAR(50),
    account_type VARCHAR(50),
    currency_code VARCHAR(10),
    account_status VARCHAR(50),
    opened_date DATE,
    closed_date DATE,
    current_balance NUMERIC(18,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.branches (
    branch_id VARCHAR(50),
    branch_name VARCHAR(150),
    city VARCHAR(100),
    region VARCHAR(100),
    branch_type VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.cards (
    card_id VARCHAR(50),
    customer_id VARCHAR(50),
    account_id VARCHAR(50),
    card_type VARCHAR(50),
    card_status VARCHAR(50),
    issued_date DATE,
    expiry_date DATE,
    credit_limit NUMERIC(18,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.merchants (
    merchant_id VARCHAR(50),
    merchant_name VARCHAR(200),
    category_code VARCHAR(50),
    city VARCHAR(100),
    country_code VARCHAR(10),
    merchant_status VARCHAR(50),
    risk_level VARCHAR(50),
    onboarded_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.merchant_categories (
    category_code VARCHAR(50),
    category_name VARCHAR(150),
    high_risk_category BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.exchange_rates (
    currency_code VARCHAR(10),
    rate_date DATE,
    rate_to_lkr NUMERIC(18,6),
    created_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.card_transactions (
    transaction_id VARCHAR(50),
    card_id VARCHAR(50),
    customer_id VARCHAR(50),
    merchant_id VARCHAR(50),
    transaction_ts TIMESTAMP,
    transaction_type VARCHAR(50),
    transaction_status VARCHAR(50),
    amount NUMERIC(18,2),
    currency_code VARCHAR(10),
    amount_lkr NUMERIC(18,2),
    channel VARCHAR(50),
    auth_code VARCHAR(100),
    is_card_present BOOLEAN,
    created_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.account_transactions (
    account_transaction_id VARCHAR(50),
    account_id VARCHAR(50),
    customer_id VARCHAR(50),
    transaction_ts TIMESTAMP,
    transaction_type VARCHAR(50),
    debit_credit_flag VARCHAR(10),
    amount NUMERIC(18,2),
    currency_code VARCHAR(10),
    balance_after NUMERIC(18,2),
    description TEXT,
    created_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.refunds (
    refund_id VARCHAR(50),
    transaction_id VARCHAR(50),
    card_id VARCHAR(50),
    customer_id VARCHAR(50),
    merchant_id VARCHAR(50),
    refund_ts TIMESTAMP,
    refund_amount NUMERIC(18,2),
    refund_reason VARCHAR(255),
    created_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.chargebacks (
    chargeback_id VARCHAR(50),
    transaction_id VARCHAR(50),
    customer_id VARCHAR(50),
    merchant_id VARCHAR(50),
    dispute_reason VARCHAR(255),
    chargeback_amount NUMERIC(18,2),
    dispute_status VARCHAR(50),
    opened_at TIMESTAMP,
    resolved_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.login_events (
    login_event_id VARCHAR(50),
    customer_id VARCHAR(50),
    device_id VARCHAR(50),
    login_ts TIMESTAMP,
    channel VARCHAR(50),
    ip_address VARCHAR(100),
    country_code VARCHAR(10),
    login_status VARCHAR(50),
    failure_reason VARCHAR(255),
    event_payload JSONB,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.device_events (
    device_event_id VARCHAR(50),
    customer_id VARCHAR(50),
    device_id VARCHAR(50),
    event_ts TIMESTAMP,
    event_type VARCHAR(50),
    os_name VARCHAR(100),
    app_version VARCHAR(50),
    ip_address VARCHAR(100),
    country_code VARCHAR(10),
    event_payload JSONB,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS raw.risk_flags (
    risk_flag_id VARCHAR(50),
    customer_id VARCHAR(50),
    transaction_id VARCHAR(50),
    flag_ts TIMESTAMP,
    risk_score NUMERIC(8,4),
    risk_reason VARCHAR(255),
    model_version VARCHAR(50),
    flag_status VARCHAR(50),
    event_payload JSONB,
    source_system VARCHAR(100),
    object_key TEXT,
    file_checksum VARCHAR(128),
    landed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(128)
);