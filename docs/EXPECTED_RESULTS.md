# RetailPulse - Expected Results and Validation Evidence

## 1. Purpose

This document describes the expected and observed outcomes for the synthetic sample dataset used to verify the RetailPulse data engineering pipeline.

The dataset contains deliberately introduced edge cases to demonstrate record validation, quarantine handling, late-arrival detection, dimensional transformation, and warehouse reconciliation.

## 2. Sample Dataset Summary

| Metric | Observed result |
|---|---:|
| Input order records | 106 |
| Accepted order records | 101 |
| Rejected order records | 5 |
| Input customer records | 1,000 |
| Accepted customer records | 1,000 |
| Rejected customer records | 0 |
| Accepted late-arriving orders | 1 |

The order reconciliation is:

`106 input = 101 accepted + 5 rejected`

## 3. Rejected Order Records

The following five records were observed in `data/quarantine/rejected_orders.csv`.

| Order ID | Validation issue | Observed rejection reason |
|---|---|---|
| O00000001 | Intentional duplicate order line | Duplicate order line |
| O_MISSING_CUSTOMER_001 | Missing customer ID | Missing required field: customer_id |
| O_NEGATIVE_QTY_001 | Negative quantity | Invalid quantity |
| O_UNKNOWN_CUSTOMER_001 | Unknown customer ID | Unknown customer_id |
| O_INVALID_PRODUCT_001 | Unknown product ID | Unknown product_id |

Only the intentionally duplicated order line shares an existing `(order_id, line_id)` key. The other four invalid records use unique order IDs so that each validation scenario is independently demonstrated.

The five records are rejected and quarantined, while the late-arriving order remains accepted.

## 4. Customer Validation

The sample run produced:

- Input customers: 1,000
- Accepted customers: 1,000
- Rejected customers: 0

The file `data/quarantine/rejected_customers.csv` contained no rejected customer records.

## 5. Late-Arriving Order

The sample dataset includes a deliberately late-arriving order.

| Field | Observed value |
|---|---|
| Order ID | O_LATE_001 |
| Customer ID | C00001 |
| Order timestamp | 2026-10-01T00:00:00Z |
| Late-arriving flag | True |
| Outcome | Accepted |

This record demonstrates that late-arriving records can be accepted while retaining a flag for monitoring and analysis.

## 6. Warehouse Expected Results

The sample pipeline produced the following dimensional model:

| Warehouse table | Expected row count |
|---|---:|
| dim_customer | 1,000 |
| dim_product | 5 |
| dim_date | 11 |
| fact_sales | 101 |

The sales fact table contains one row per accepted order line.

## 7. Data Quality Monitoring

The sample run completed seven monitoring checks:

1. Accepted order count versus warehouse fact count.
2. Duplicate fact keys.
3. Required fact fields.
4. Customer referential integrity.
5. Product referential integrity.
6. Revenue calculation.
7. Input order reconciliation.

Observed result:

| Metric | Result |
|---|---:|
| Total checks | 7 |
| Passed | 7 |
| Failed | 0 |
| Overall status | PASS |

## 8. Reproducibility

From the project root, activate the virtual environment, install dependencies, and run:

```powershell
python -m pip install -r requirements.txt
python scripts\generate_data.py --orders 100 --customers 1000 --seed 42
python scripts\run_pipeline.py
python -m pytest -v
```

The generator creates synthetic input data. The pipeline produces processed records, quarantine files, Parquet warehouse datasets, DuckDB tables, analytical results, and monitoring reports.

The expected counts above correspond to the committed sample dataset and observed sample run. Execution time can vary by machine and environment.

## 9. Evidence Files

The repository includes sample pipeline evidence under `outputs/sample_outputs/`:

- `validation_report.json`
- `monitoring_report.json`
- `pipeline_report.json`
- `reconciliation.txt`

The detailed data dictionary and design decisions are documented in `docs/DATA_DICTIONARY_AND_DESIGN.md`.

## 10. Limitations

- The dataset is synthetic and does not represent real retail transactions.
- Each deliberately invalid sample order demonstrates one intended rejection scenario; real records can contain multiple validation failures.
- The sample results describe the current implementation and sample data; different generated inputs can produce different counts.
- Late-arrival detection uses the configured validation cutoff and does not imply that the record is rejected.
