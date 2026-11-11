
# RetailPulse – End-to-End Data Engineering Platform

An end-to-end data engineering project that ingests retail data from multiple sources, validates data quality, transforms records into a dimensional warehouse, and provides analytical insights using Python and DuckDB.

## 1. Project Overview

RetailPulse is a batch data engineering platform designed to demonstrate a complete retail data processing workflow.

The platform processes order and customer data from CSV and JSON sources, identifies invalid records, transforms accepted data into dimensional tables, loads the data into DuckDB, and executes analytical queries.

It also includes automated data quality monitoring, pipeline execution reports, and unit tests.

## 2. Key Features

- Multi-source data ingestion (CSV and JSON).
- Data validation and rejection handling.
- Detection of duplicate records and invalid references.
- Future timestamp validation.
- Late-arriving data identification.
- Dimensional data modeling.
- Parquet-based intermediate storage.
- DuckDB analytical warehouse.
- Idempotent warehouse loading.
- Automated data quality monitoring.
- Analytical SQL queries.
- Pipeline execution-time monitoring.
- Automated unit and warehouse tests.

## 3. Architecture

```text
       CSV Orders       JSON Customers
            |                 |
            +--------+--------+
                     |
                     v
             DATA INGESTION
                     |
                     v
             DATA VALIDATION
                /        \
               v          v
          Accepted      Rejected
           Records      Records
               |
               v
          TRANSFORMATION
               |
               v
       DIMENSIONAL MODEL
               |
               v
         PARQUET STORAGE
               |
               v
          DUCKDB WAREHOUSE
               |
          +----+------+
          |           |
          v           v
      MONITORING   ANALYTICS
          |           |
          +-----+-----+
                |
                v
         PIPELINE REPORT
```

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10 | Pipeline development |
| Pandas | Data processing and validation |
| DuckDB | Analytical data warehouse |
| PyArrow | Parquet storage |
| Pytest | Automated testing |
| JSON / CSV | Source data formats |
| SQL | Analytical queries |
| Git | Version control |

## 5. Project Structure

```text
retailpulse-data-engineering/
|
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── quarantine/
│   └── sample_outputs/
|
├── database/
|
├── src/
│   └── retailpulse/
│       ├── ingestion/
│       ├── validation/
│       ├── transformation/
│       ├── warehouse/
│       ├── monitoring/
│       └── analytics/
|
├── scripts/
│   ├── generate_data.py
│   ├── run_ingestion.py
│   ├── run_validation.py
│   ├── run_transformation.py
│   ├── run_warehouse.py
│   ├── run_monitoring.py
│   ├── run_analytics.py
│   └── run_pipeline.py
|
├── tests/
│   ├── test_validation.py
│   └── test_warehouse.py
|
├── outputs/
├── docs/
├── prompt_history/
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## 6. Data Sources

The platform supports two input sources.

### Orders CSV

Contains order-level information:

- order_id
- line_id
- customer_id
- product_id
- product_name
- category
- order_timestamp
- quantity
- unit_price

### Customers JSON

Contains customer information:

- customer_id
- customer_name
- email
- city
- registration_date

Synthetic data is generated locally for reproducible testing.

## 7. Data Validation

The validation layer checks:

- Required fields.
- Missing values.
- Duplicate order-line keys.
- Invalid timestamps.
- Future-dated orders.
- Negative quantities.
- Invalid prices.
- Unknown customer references.
- Invalid product references.

Invalid records are separated into quarantine outputs with rejection reasons.

Late-arriving records are identified and flagged rather than automatically rejected.

## 8. Dimensional Data Model

The warehouse contains four tables.

| Table | Description |
|---|---|
| dim_customer | Customer dimension |
| dim_product | Product dimension |
| dim_date | Date dimension |
| fact_sales | Sales fact table |

**Fact table grain:** One row per order line.

The fact table includes sales measures and relevant customer, product, and date keys.

## 9. Data Quality Monitoring

The monitoring module executes seven checks:

1. Accepted orders versus warehouse fact row count.
2. Duplicate fact keys.
3. Missing required fact fields.
4. Customer referential integrity.
5. Product referential integrity.
6. Revenue calculation consistency.
7. Input, accepted, and rejected record reconciliation.

Each check produces a PASS or FAIL result.

## 10. Analytical Capabilities

The platform executes analytical queries for:

- Total sales and revenue.
- Total units sold.
- Average order-line revenue.
- Revenue by product and category.
- Top 10 customers by revenue.
- Late-arriving order counts.

## 11. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (optional)

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/retailpulse-data-engineering.git

cd retailpulse-data-engineering
```

### Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 12. Generate Sample Data

Generate 100,000 synthetic order records and 1,000 customers:

```bash
python -m scripts.generate_data --orders 100000 --seed 42
```

The generator also introduces controlled data quality edge cases.

## 13. Run the Complete Pipeline

Execute all six pipeline stages:

```bash
python -m scripts.run_pipeline
```

The pipeline executes:

1. Ingestion
2. Validation
3. Transformation
4. Warehouse loading
5. Monitoring
6. Analytics

Execution results are written to the outputs directory.

## 14. Run Automated Tests

```bash
python -m pytest -v
```

The test suite covers validation scenarios and warehouse loading behavior, including idempotency.

## 15. Performance Benchmark

Test environment:

- Operating system: Windows 11
- Python: 3.10.11
- Input orders: 100,006
- Input customers: 1,000

Verified benchmark from a local execution:

| Metric | Result |
|---|---:|
| Input order records | 100,006 |
| Accepted orders | 100,001 |
| Rejected orders | 5 |
| Fact sales rows | 100,001 |
| Late-arriving orders | 1 |
| Data quality checks | 7/7 passed |
| Pipeline stages | 6/6 successful |
| Total pipeline time | 6.33 seconds |
| Automated tests | 17 passed |

The benchmark is from one local run and is environment-dependent.

## 16. Pipeline Observability

The pipeline generates a JSON execution report containing:

- Pipeline status.
- Start and end timestamps.
- Total execution duration.
- Completed stages.
- Failed stage, if applicable.
- Individual stage durations.

Report location:

```text
outputs/pipeline_report.json
```

Additional reports:

```text
outputs/validation_report.json
outputs/monitoring_report.json
```

## 17. Idempotency

The warehouse loader uses table replacement from the generated Parquet datasets rather than blindly appending records.

This prevents duplicate fact records when the same warehouse load is executed again.

Warehouse idempotency is verified through automated tests.

## 18. Current Limitations

- The pipeline currently processes batch data rather than streaming events.
- Input files are local CSV and JSON files.
- Automatic retry and checkpoint-based recovery are not implemented.
- The warehouse is a local DuckDB database.
- Synthetic data is used for reproducible demonstrations.
- Pipeline execution time depends on the local environment and dataset.

## 19. Future Improvements

- Incremental data processing.
- Checkpoint-based recovery.
- Configurable late-arrival watermark.
- Structured application logging.
- More extensive integration tests.
- Docker-based deployment.
- Cloud object storage integration.
- Workflow orchestration.

## 20. Author

**K Vishnu**

B.E. – Information Science and Engineering  
Bangalore Institute of Technology

GitHub: https://github.com/kvishnuchowdary78-design

---

**RetailPulse – Building reliable data pipelines through validation, transformation, monitoring, and analytics.**
