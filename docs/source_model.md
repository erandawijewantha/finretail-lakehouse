# FinRetail Lakehouse - Source Model

## 1. Project Domain

This project simulates a financial-retail transaction platform with banking-like transaction behavior, merchant activity, customer accounts, card payments, refunds, chargebacks, digital login events, and risk signals.

The goal is to generate complex multi-source data for a production-style data engineering pipeline using object storage, Airflow, PostgreSQL, and Power BI.

---

## 2. Source Systems

| Source System | Description | Format | Landing Path |
|---|---|---|---|
| core_banking | customers, accounts, branches | Parquet | raw/core_banking/ |
| card_processor | card transactions, refunds, chargebacks | CSV | raw/card_processor/ |
| digital_channels | login events, device events | JSON | raw/digital_channels/ |
| merchant_system | merchants and merchant categories | Parquet | raw/merchant_system/ |
| risk_engine | risk flags and suspicious activity scores | JSON | raw/risk_engine/ |
| reference_data | exchange rates, calendar, country codes | CSV | raw/reference_data/ |

---

## 3. Core Entities

### Master / Reference
- customers
- accounts
- branches
- cards
- merchants
- merchant_categories
- exchange_rates

### Transaction / Event
- card_transactions
- account_transactions
- refunds
- chargebacks
- login_events
- device_events
- risk_flags

---

## 4. Entity Summary

| Entity | Business Key | Source System | Format | Load Pattern | SCD Candidate |
|---|---|---|---|---|---|
| customers | customer_id | core_banking | Parquet | upsert | yes |
| accounts | account_id | core_banking | Parquet | upsert | yes |
| branches | branch_id | core_banking | Parquet | upsert | low |
| cards | card_id | card_processor | CSV | upsert | yes |
| merchants | merchant_id | merchant_system | Parquet | upsert | yes |
| merchant_categories | category_code | merchant_system | Parquet | full/upsert | no |
| exchange_rates | currency_code + rate_date | reference_data | CSV | append | no |
| card_transactions | transaction_id | card_processor | CSV | append | no |
| account_transactions | account_transaction_id | core_banking | Parquet | append | no |
| refunds | refund_id | card_processor | CSV | append | no |
| chargebacks | chargeback_id | card_processor | CSV | append/update | no |
| login_events | login_event_id | digital_channels | JSON | append | no |
| device_events | device_event_id | digital_channels | JSON | append | no |
| risk_flags | risk_flag_id | risk_engine | JSON | append/update | no |

---

## 5. Incremental Strategy

### Append-only
- card_transactions
- account_transactions
- refunds
- login_events
- device_events
- exchange_rates

### Upsert
- customers
- accounts
- branches
- cards
- merchants
- chargebacks
- risk_flags

### SCD Type 2 Candidates
- customers
- accounts
- cards
- merchants

---

## 6. Real-World Data Problems to Simulate

The generator must create:

- duplicate transaction events
- late-arriving transactions
- failed card authorizations
- refunded transactions
- chargeback disputes
- reversed account entries
- inactive accounts/cards
- customer address/segment changes
- merchant category changes
- suspicious login patterns
- multiple devices per customer
- high-risk transactions
- schema drift in JSON event payloads
- missing/null keys for reject testing
- orphan events for data quality checks

---

## 7. Landing Path Convention

Files should land in MinIO using this convention:

```text
s3://finretail-lakehouse/raw/{source_system}/{entity_name}/dt=YYYY-MM-DD/{entity_name}_{batch_id}.{ext}