# RetailPulse - Data Dictionary and Design Documentation



## 1. Project Overview



RetailPulse is an end-to-end retail data engineering platform that ingests customer and order data, validates records, transforms accepted data into a dimensional model, loads the model into DuckDB, and exposes analytical queries and data-quality monitoring.



### Data Sources



| Source | Format | Description |

|---|---|---|

| Orders | CSV | Retail order-line transactions |

| Customers | JSON | Customer master records |



The project uses Python, Pandas, Parquet and DuckDB.



## 2. Architecture and Data Flow



The platform follows a modular batch-processing architecture.



1\. \*\*Ingestion:\*\* Load orders from CSV and customers from JSON.

2\. \*\*Validation:\*\* Check schemas, required fields, numeric values, timestamps, duplicate records and referential integrity.

3\. \*\*Quarantine:\*\* Separate rejected records and preserve their rejection reasons.

4\. \*\*Transformation:\*\* Build customer, product and date dimensions and the sales fact table.

5\. \*\*Storage:\*\* Write transformed datasets as Parquet files.

6\. \*\*Warehouse:\*\* Load Parquet datasets into DuckDB.

7\. \*\*Monitoring:\*\* Execute data-quality and reconciliation checks.

8\. \*\*Analytics:\*\* Execute analytical SQL queries against the warehouse.



### Logical Data Flow



```text

Orders CSV       Customers JSON

&#x20;    |                  |

&#x20;    +--------+---------+

&#x20;             |

&#x20;         Ingestion

&#x20;             |

&#x20;         Validation

&#x20;          /      \\

&#x20;     Accepted   Rejected

&#x20;        |           |

&#x20;        |        Quarantine

&#x20;        |

&#x20;    Transformation

&#x20;        |

&#x20;  Parquet Datasets

&#x20;        |

&#x20;   DuckDB Warehouse

&#x20;        |

&#x20;   +----+------+

&#x20;   |           |

&#x20;Monitoring  Analytics

```



## 3. Dimensional Data Model



RetailPulse uses a star-schema-style dimensional model with one fact table and three dimension tables.



### Fact Table



`fact\_sales`



\*\*Grain:\*\* One row per order line, identified by the combination of `order\_id` and `line\_id`.



### Dimension Tables



\- `dim\_customer`: Customer attributes.

\- `dim\_product`: Product attributes derived from accepted order records.

\- `dim\_date`: Calendar attributes derived from valid order timestamps.



### Relationships



| Fact column | Dimension column | Relationship |

|---|---|---|

| customer\_id | dim\_customer.customer\_id | Many-to-one |

| product\_id | dim\_product.product\_id | Many-to-one |

| date\_key | dim\_date.date\_key | Many-to-one |



## 4. Data Dictionary



The following types describe the transformed Pandas/Parquet data model. Exact physical database types may be inferred by DuckDB during table creation.



### 4.1 dim\_customer



| Column | Logical type | Key | Description |

|---|---|---|---|

| customer\_id | String | Natural key | Unique customer identifier |

| customer\_name | String | | Customer's name |

| email | String | | Customer email address |

| city | String | | Customer city |

| registration\_date | Date | | Customer registration date |



\*\*Transformation rules:\*\*

\- Customer identifiers, names and cities are trimmed.

\- Registration dates are converted to date values.

\- Duplicate customer IDs are removed, keeping the first occurrence.



### 4.2 dim\_product



| Column | Logical type | Key | Description |

|---|---|---|---|

| product\_id | String | Natural key | Product identifier |

| product\_name | String | | Product name |

| category | String | | Product category |

| observed\_unit\_price | Numeric | | Unit price observed in the source order records |



\*\*Transformation rules:\*\*

\- Product records are derived from accepted order records.

\- Duplicate product IDs are removed, keeping the first occurrence.

\- `unit\_price` is renamed to `observed\_unit\_price`.



\*\*Design consideration:\*\* The current implementation does not maintain historical product prices or product versions. The observed price is not a guaranteed current catalogue price.



### 4.3 dim\_date



| Column | Logical type | Key | Description |

|---|---|---|---|

| full\_date | Date | | Calendar date |

| date\_key | Integer | Primary key | Date in YYYYMMDD format |

| year | Integer | | Calendar year |

| month | Integer | | Calendar month number |

| day | Integer | | Day of month |

| quarter | Integer | | Calendar quarter |

| month\_name | String | | Full month name |



\*\*Transformation rules:\*\*

\- Order timestamps are parsed in UTC.

\- Distinct order dates are extracted.

\- `date\_key` is generated using YYYYMMDD.

\- Year, month, day, quarter and month name are derived from the date.



### 4.4 fact\_sales



| Column | Logical type | Key | Description |

|---|---|---|---|

| order\_id | String | Composite key | Order identifier |

| line\_id | Integer | Composite key | Order-line identifier |

| customer\_id | String | Foreign key | Customer reference |

| product\_id | String | Foreign key | Product reference |

| date\_key | Integer | Foreign key | Calendar date reference |

| order\_timestamp | UTC Timestamp | | Order event timestamp |

| quantity | Integer | | Units purchased |

| unit\_price | Numeric | | Unit price per item |

| revenue | Numeric | | Quantity multiplied by unit price |

| is\_late\_arriving | Boolean | | Late-arrival indicator |

| run\_id | String | | Pipeline validation run identifier |

| source\_file | String | | Source filename |

| source\_record | Integer | | Original source record position |



\*\*Derived fields:\*\*



```text

revenue = quantity \* unit\_price



date\_key = YYYYMMDD derived from order\_timestamp

```



Revenue is rounded to two decimal places.



## 5. Data Validation Rules



### Customer validation



\- Required customer columns must exist.

\- Customer ID, name, email, city and registration date must be populated.

\- Registration date must be parseable.

\- Duplicate customer IDs are rejected.



### Order validation



\- Required order columns must exist.

\- Required fields must not be null or blank.

\- Line ID must be numeric and greater than zero.

\- Quantity must be numeric and greater than zero.

\- Unit price must be numeric and non-negative.

\- Order timestamp must be valid.

\- Future timestamps are rejected.

\- Customer references must match accepted customer IDs.

\- Product identifiers must belong to the configured valid product set.

\- Duplicate `(order\_id, line\_id)` combinations are rejected.



### Late-arrival detection



The current implementation calculates the cutoff as:



```text

late\_cutoff = latest\_valid\_event\_timestamp - 30 days

```



A valid event timestamp earlier than this cutoff is flagged as late-arriving.



The watermark is calculated from valid, non-future timestamps in the current batch.



Late-arriving records are flagged, not automatically rejected.



## 6. Naming Conventions



| Convention | Usage | Example |

|---|---|---|

| snake\_case | Python functions and columns | `order\_timestamp` |

| dim\_ prefix | Dimension tables | `dim\_customer` |

| fact\_ prefix | Fact tables | `fact\_sales` |

| \*\_id | Business identifiers | `customer\_id` |

| \*\_key | Warehouse date key | `date\_key` |

| is\_\* | Boolean flags | `is\_late\_arriving` |

| \*\_report.json | Execution reports | `monitoring\_report.json` |



## 7. Assumptions



1\. Orders are represented at order-line level.

2\. The combination of order ID and line ID uniquely identifies an order line.

3\. Customer identifiers are used as natural keys.

4\. Product identifiers are validated against a configured synthetic product catalogue.

5\. Order timestamps are interpreted in UTC.

6\. Revenue is calculated as quantity multiplied by unit price.

7\. Rejected records should remain available for inspection in quarantine outputs.

8\. The current product dimension is derived from accepted order data.

9\. The platform processes batch inputs rather than streaming events.

10\. Synthetic sample data is used for reproducible demonstration.



## 8. Design Decisions and Trade-offs



### Pandas for transformation



Pandas provides convenient tabular processing and validation capabilities for the current project scale.



\*\*Trade-off:\*\* Large datasets may eventually require distributed processing or more memory-efficient processing.



### Parquet for intermediate warehouse datasets



Parquet provides a columnar storage format for transformed datasets.



\*\*Trade-off:\*\* Intermediate validation files currently use CSV, which is easier to inspect but less efficient for larger data volumes.



### DuckDB for analytical storage



DuckDB provides a lightweight embedded analytical database that can run locally without a separate database server.



\*\*Trade-off:\*\* The current design is intended for local batch analytics rather than a distributed, multi-user production warehouse.



### Replacing warehouse tables



The loader currently uses `CREATE OR REPLACE TABLE` for each warehouse table. This supports repeatable loads without appending duplicate records.



\*\*Limitation:\*\* The four table replacements are currently sequential and are not enclosed in one explicit transaction. A failure partway through loading could leave a partially updated warehouse. Transactional loading is a planned reliability improvement.



## 9. Performance and Optimization



A 100K-order synthetic dataset was used for performance evaluation.



The recorded Windows benchmark was approximately 6.33 seconds for the complete pipeline. Actual execution time depends on hardware, operating system and environment.



The validation stage is a potential optimization target because validation rules are applied through several Pandas operations.



Potential improvement:



\- Reduce repeated DataFrame operations.

\- Reuse parsed numeric and timestamp columns.

\- Evaluate vectorized validation expressions.

\- Benchmark CSV versus Parquet for intermediate storage.



Any optimization should preserve validation results and rejection reasons.



## 10. Reliability, Recovery and Limitations



### Current capabilities



\- Rejected records are separated into quarantine files.

\- Pipeline stages report execution status and timing.

\- Warehouse table replacement avoids duplicate accumulation during repeated full loads.

\- Data-quality monitoring checks row counts, duplicate keys, required values, references and revenue calculations.

\- Unit tests cover validation and warehouse loading.



### Current limitations



\- Warehouse table replacements are not yet wrapped in a single transaction.

\- There is no automated retry mechanism.

\- Pipeline reports are overwritten rather than retained as a historical run archive.

\- Product reference data is currently hardcoded in the validator.

\- Empty-batch behavior needs an explicit operational warning.

\- Automated ingestion and end-to-end pipeline failure tests can be expanded.



### Future improvements



1\. Add transactional warehouse loading and rollback tests.

2\. Add structured application logging.

3\. Preserve run history and rejected-record run identifiers.

4\. Add ingestion, transformation and end-to-end integration tests.

5\. Externalize product reference data.

6\. Add explicit empty-input checks.

7\. Document retry, restart and backfill procedures.



## 11. Reproducibility and Evidence



Sample execution reports are stored in:



```text

outputs/sample\_outputs/

```



The directory contains:



\- `validation\_report.json`

\- `monitoring\_report.json`

\- `pipeline\_report.json`

\- `reconciliation.txt`



These files provide evidence of the sample dataset execution and its reconciliation results.



The sample run processed 106 input orders, accepted 101, rejected 5, and passed all seven monitoring checks. All six pipeline stages completed successfully.



## 12. Conclusion



RetailPulse demonstrates an end-to-end batch data engineering workflow, including ingestion, validation, transformation, dimensional modeling, analytical storage, monitoring, reconciliation and automated testing.



The design prioritizes reproducibility, data quality, clear modular structure and local execution. The limitations and future improvements documented here identify the next steps toward a more production-ready implementation.


