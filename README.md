# RetailPulse – End-to-End Data Engineering Platform

An end-to-end data engineering platform that ingests retail data from multiple sources, validates data quality, transforms records into a dimensional warehouse, and provides analytical insights using Python and DuckDB.

## 1. Project Overview

RetailPulse is a batch data engineering platform designed to demonstrate a complete retail data processing workflow.

The platform processes order and customer data from CSV and JSON sources, identifies invalid records, transforms accepted data into dimensional tables, loads the data into DuckDB, and executes analytical queries.

It also includes automated data quality monitoring, pipeline execution reports, transactional warehouse loading, and automated tests.

## 2. Key Features

- Multi-source data ingestion (CSV and JSON).
- Data validation and rejection handling.
- Detection of duplicate records and invalid references.
- Future timestamp validation.
- Late-arriving data identification.
- Dimensional data modeling.
- Parquet-based intermediate storage.
- DuckDB analytical warehouse.
- Idempotent and transactional warehouse loading.
- Automated data quality monitoring.
- Analytical SQL queries.
- Pipeline execution-time monitoring.
- Automated tests covering ingestion, validation, transformation, pipeline execution, and warehouse loading.

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
             Accepted    Rejected
              Records    Records
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
             +---+------+
             |          |
             v          v
          MONITORING  ANALYTICS
             |          |
             +----+-----+
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
│
├── data/
│   └── sample_inputs/
│       ├── orders.csv
│       └── customers.json
│
├── docs/
│   ├── DATA_DICTIONARY_AND_DESIGN.md
│   └── EXPECTED_RESULTS.md
│
├── outputs/
│   └── sample_outputs/
│       ├── validation_report.json
│       ├── monitoring_report.json
│       ├── pipeline_report.json
│       └── reconciliation.txt
│
├── prompt_history/
│   ├── README.md
│   └── chatgpt_prompts.md
│
├── scripts/
│   ├── generate_data.py
│   ├── run_ingestion.py
│   ├── run_validation.py
│   ├── run_transformation.py
│   ├── run_warehouse.py
│   ├── run_monitoring.py
│   ├── run_analytics.py
│   ├── run_pipeline.py
│   └── verify_data.py
│
├── src/
│   └── retailpulse/
│       ├── ingestion/
│       │   └── loader.py
│       ├── validation/
│       │   └── validator.py
│       ├── transformation/
│       │   └── transform.py
│       ├── warehouse/
│       │   └── loader.py
│       ├── monitoring/
│       └── analytics/
│           └── queries.py
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_pipeline.py
│   ├── test_transformation.py
│   ├── test_validation.py
│   └── test_warehouse.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── pytest.ini
```

Generated raw data, processed files, Parquet files, DuckDB databases, and execution reports are created locally when the pipeline runs. The reproducible sample inputs and selected sample evidence reports are committed to Git.

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

The data dictionary, naming conventions, assumptions, design decisions, and trade-offs are documented in [DATA_DICTIONARY_AND_DESIGN.md](docs/DATA_DICTIONARY_AND_DESIGN.md).

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

- Python 3.10 or later.
- Git.
- Visual Studio Code (optional).

### Clone the repository

```bash
git clone https://github.com/kvishnuchowdary78-design/retailpulse-data-engineering.git
cd retailpulse-data-engineering
```

### Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 12. Run Using Included Sample Data

The repository includes small synthetic sample datasets for quick verification.

Copy the sample files into the raw input directory.

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Force data\raw
Copy-Item data\sample_inputs\orders.csv data\raw\orders.csv -Force
Copy-Item data\sample_inputs\customers.json data\raw\customers.json -Force
```

**Linux / macOS:**

```bash
mkdir -p data/raw
cp data/sample_inputs/orders.csv data/raw/orders.csv
cp data/sample_inputs/customers.json data/raw/customers.json
```

Run the complete pipeline:

```bash
python -m scripts.run_pipeline
```

The included sample dataset contains 106 order records, including controlled data quality edge cases.

Expected sample results:

| Metric | Result |
|---|---:|
| Input orders | 106 |
| Accepted orders | 101 |
| Rejected orders | 5 |
| Accepted customers | 1,000 |
| Fact sales rows | 101 |
| Monitoring checks passed | 7/7 |
| Pipeline stages successful | 6/6 |

See [EXPECTED_RESULTS.md](docs/EXPECTED_RESULTS.md) and [sample execution evidence](outputs/sample_outputs/reconciliation.txt) for detailed results.

## 13. Generate a Larger Dataset

To generate 100,000 synthetic order records and 1,000 customers:

```bash
python -m scripts.generate_data --orders 100000 --customers 1000 --seed 42
```

The generator introduces controlled data quality edge cases for validation testing.

Run the complete pipeline:

```bash
python -m scripts.run_pipeline
```

## 14. Pipeline Execution

The pipeline executes six stages:

1. Ingestion
2. Validation
3. Transformation
4. Warehouse loading
5. Monitoring
6. Analytics

Execution results and stage timings are written to the local outputs directory.

## 15. Run Automated Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The current test suite contains **37 passing tests** covering:

- Ingestion and source schema handling.
- Missing files and malformed JSON.
- Data validation scenarios.
- Transformation and dimensional data creation.
- Pipeline success and failure handling.
- Warehouse loading, idempotency, and transaction rollback.

## 16. Performance Benchmark

Test environment:

- Operating system: Windows 11.
- Python: 3.10.11.
- Input orders: 100,006.
- Input customers: 1,000.

Verified local benchmark:

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
| Automated tests | 37 passed |

The benchmark represents a local execution and is environment-dependent. The 100K benchmark timing and the sample dataset timing are separate executions.

## 17. Pipeline Observability

The pipeline generates a JSON execution report containing:

- Pipeline status.
- Start and end timestamps.
- Total execution duration.
- Completed stages.
- Failed stage, if applicable.
- Individual stage durations.

Local report locations:

```text
outputs/pipeline_report.json
outputs/validation_report.json
outputs/monitoring_report.json
```

Selected sample reports are committed under `outputs/sample_outputs/`.

The current implementation uses console output and JSON reports rather than structured application logging.

## 18. Idempotency and Transactional Loading

The warehouse loader uses table replacement from generated Parquet datasets rather than blindly appending records.

This prevents duplicate fact records when the same warehouse load is executed again.

The warehouse table replacements are performed inside a DuckDB transaction. If a table replacement fails, the transaction is rolled back so that the warehouse does not retain a partially replaced set of tables.

Automated tests verify repeat-load behavior and rollback on a simulated failed load.

## 19. Recovery, Restart, and Backfill

### Rerun and restart

The pipeline is orchestrated as a sequence of stages. If a stage fails, the pipeline records the failure and exits with a non-zero status.

To restart, correct the issue and rerun the complete pipeline from the project root:

```bash
python -m scripts.run_pipeline
```

The pipeline starts again from ingestion and rebuilds its downstream outputs from the current raw input files. Warehouse table replacements are transactional, so a failed warehouse load rolls back its table replacements.

This is a full pipeline rerun strategy; the current implementation does not provide automatic stage-level retry or checkpoint-based resumption.

### Backfill

To process a historical batch, place the intended historical orders CSV and corresponding customer JSON in `data/raw/`, using the expected filenames and schemas. Then rerun the complete pipeline.

The current backfill approach is a full rebuild for the supplied batch, not an incremental merge into historical warehouse data. Preserve previous source files and reports separately if historical run retention is required.

## 20. Optimization and Design Trade-offs

### Parquet intermediate storage

The transformation stage writes dimensional and fact datasets as Parquet before warehouse loading.

Parquet is a columnar storage format suited to analytical workloads. It supports typed data representation and allows analytical engines such as DuckDB to work with selected columns efficiently.

This is the selected intermediate storage optimization in RetailPulse. The project does not claim a measured CSV-versus-Parquet speedup because a controlled comparative benchmark has not been performed.

Other design trade-offs and assumptions are described in [DATA_DICTIONARY_AND_DESIGN.md](docs/DATA_DICTIONARY_AND_DESIGN.md).

## 21. Current Limitations

- The pipeline currently processes batch data rather than streaming events.
- Input files are local CSV and JSON files.
- Automatic retry and checkpoint-based recovery are not implemented.
- Backfill currently uses a full rebuild rather than incremental historical merging.
- The warehouse is a local DuckDB database.
- Synthetic data is used for reproducible demonstrations.
- Structured application logging is not implemented; execution details are printed to the console and recorded in reports.
- Pipeline execution time depends on the local environment and dataset.

## 22. Future Improvements

- Incremental data processing.
- Checkpoint-based recovery.
- Configurable late-arrival watermark.
- Structured application logging.
- More extensive integration tests.
- Docker-based deployment.
- Cloud object storage integration.
- Workflow orchestration.

## 23. AI Usage Disclosure

ChatGPT was used as a development assistant for code suggestions, debugging, testing guidance, and documentation.

The prompt history is maintained in the `prompt_history/` directory. Prompt descriptions are identified as reconstructed summaries where they are not verbatim.

The project author is responsible for understanding and verifying the final implementation.

## 24. Author

**K Vishnu**

B.E. – Information Science and Engineering  
Bangalore Institute of Technology

GitHub: https://github.com/kvishnuchowdary78-design

**Repository:** https://github.com/kvishnuchowdary78-design/retailpulse-data-engineering

---

**RetailPulse – Building reliable data pipelines through validation, transformation, monitoring, and analytics.**
