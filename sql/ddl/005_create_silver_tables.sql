CREATE TABLE IF NOT EXISTS silver.dim_customer_current AS
SELECT * FROM bronze.customers WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.dim_account_current AS
SELECT * FROM bronze.accounts WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.dim_card_current AS
SELECT * FROM bronze.cards WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.dim_merchant_current AS
SELECT * FROM bronze.merchants WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.card_transactions_clean AS
SELECT * FROM bronze.card_transactions WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.account_transactions_clean AS
SELECT * FROM bronze.account_transactions WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.refunds_clean AS
SELECT * FROM bronze.refunds WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.chargebacks_clean AS
SELECT * FROM bronze.chargebacks WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.login_events_clean AS
SELECT * FROM bronze.login_events WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.device_events_clean AS
SELECT * FROM bronze.device_events WHERE 1=0;

CREATE TABLE IF NOT EXISTS silver.risk_flags_clean AS
SELECT * FROM bronze.risk_flags WHERE 1=0;