CREATE TABLE IF NOT EXISTS gold.dim_customer AS
SELECT
    customer_id,
    full_name,
    gender,
    date_of_birth,
    city,
    region,
    customer_segment,
    risk_tier,
    kyc_status,
    is_active
FROM silver.dim_customer_current
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.dim_account AS
SELECT
    account_id,
    customer_id,
    branch_id,
    account_type,
    currency_code,
    account_status,
    opened_date,
    closed_date,
    current_balance
FROM silver.dim_account_current
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.dim_card AS
SELECT
    card_id,
    customer_id,
    account_id,
    card_type,
    card_status,
    issued_date,
    expiry_date,
    credit_limit
FROM silver.dim_card_current
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.dim_merchant AS
SELECT
    merchant_id,
    merchant_name,
    category_code,
    city,
    country_code,
    merchant_status,
    risk_level
FROM silver.dim_merchant_current
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.fact_card_transactions AS
SELECT
    transaction_id,
    card_id,
    customer_id,
    merchant_id,
    transaction_ts::DATE AS transaction_date,
    transaction_ts,
    transaction_type,
    transaction_status,
    amount,
    currency_code,
    amount_lkr,
    channel,
    is_card_present
FROM silver.card_transactions_clean
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.fact_account_transactions AS
SELECT
    account_transaction_id,
    account_id,
    customer_id,
    transaction_ts::DATE AS transaction_date,
    transaction_ts,
    transaction_type,
    debit_credit_flag,
    amount,
    currency_code,
    balance_after
FROM silver.account_transactions_clean
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.fact_refunds AS
SELECT
    refund_id,
    transaction_id,
    card_id,
    customer_id,
    merchant_id,
    refund_ts::DATE AS refund_date,
    refund_ts,
    refund_amount,
    refund_reason
FROM silver.refunds_clean
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.fact_chargebacks AS
SELECT
    chargeback_id,
    transaction_id,
    customer_id,
    merchant_id,
    opened_at::DATE AS opened_date,
    opened_at,
    resolved_at,
    dispute_reason,
    chargeback_amount,
    dispute_status
FROM silver.chargebacks_clean
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.fact_risk_flags AS
SELECT
    risk_flag_id,
    customer_id,
    transaction_id,
    flag_ts::DATE AS flag_date,
    flag_ts,
    risk_score,
    risk_reason,
    model_version,
    flag_status
FROM silver.risk_flags_clean
WHERE 1 = 0;

CREATE TABLE IF NOT EXISTS gold.mart_daily_transaction_summary (
    transaction_date DATE,
    channel VARCHAR(50),
    transaction_status VARCHAR(50),
    total_transactions BIGINT,
    total_amount_lkr NUMERIC(18,2),
    avg_amount_lkr NUMERIC(18,2),
    PRIMARY KEY (transaction_date, channel, transaction_status)
);

CREATE TABLE IF NOT EXISTS gold.mart_merchant_risk_summary (
    merchant_id VARCHAR(50) PRIMARY KEY,
    total_transactions BIGINT,
    total_amount_lkr NUMERIC(18,2),
    refund_count BIGINT,
    refund_amount NUMERIC(18,2),
    chargeback_count BIGINT,
    chargeback_amount NUMERIC(18,2),
    avg_risk_score NUMERIC(8,4)
);

CREATE TABLE IF NOT EXISTS gold.mart_customer_risk_summary (
    customer_id VARCHAR(50) PRIMARY KEY,
    total_card_transactions BIGINT,
    total_card_amount_lkr NUMERIC(18,2),
    total_account_transactions BIGINT,
    refund_count BIGINT,
    chargeback_count BIGINT,
    risk_flag_count BIGINT,
    avg_risk_score NUMERIC(8,4)
);