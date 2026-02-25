---
name: data-engineering
description: Data engineering and ETL pipeline patterns covering data extraction, transformation, loading, batch and stream processing, data validation, schema evolution, pipeline orchestration, data quality checks, and integration with tools like Apache Kafka, dbt, Airflow, and modern Python data stack.
---

# Data Engineering & ETL

This skill should be used when building data pipelines, ETL/ELT workflows, or data processing systems. It covers extraction, transformation, loading patterns, and pipeline orchestration.

## When to Use This Skill

Use this skill when you need to:

- Build ETL/ELT data pipelines
- Process streaming or batch data
- Validate and clean data
- Orchestrate data workflows
- Design data warehouse schemas
- Implement data quality checks

## ETL Pipeline Architecture

```
DATA PIPELINE PATTERNS:

ETL (Extract-Transform-Load):
  Source → Extract → Transform → Load → Warehouse
  Best for: Complex transformations, data cleansing before load

ELT (Extract-Load-Transform):
  Source → Extract → Load → Transform (in warehouse)
  Best for: Cloud warehouses (BigQuery, Snowflake), raw data lake

Streaming:
  Source → Stream (Kafka) → Process → Sink
  Best for: Real-time analytics, event-driven systems
```

## Python ETL with Pandas

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

def extract_csv(path: str) -> pd.DataFrame:
    """Extract data from CSV with type inference."""
    return pd.read_csv(
        path,
        parse_dates=["created_at", "updated_at"],
        dtype={"id": str, "amount": float},
    )

def extract_api(url: str, params: dict) -> pd.DataFrame:
    """Extract data from REST API with pagination."""
    import requests
    all_data = []
    page = 1
    while True:
        response = requests.get(url, params={**params, "page": page}, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data["results"]:
            break
        all_data.extend(data["results"])
        page += 1
    return pd.DataFrame(all_data)

def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform order data."""
    return (
        df
        .dropna(subset=["customer_id", "amount"])
        .assign(
            amount=lambda x: x["amount"].clip(lower=0),
            order_date=lambda x: pd.to_datetime(x["order_date"]),
            year_month=lambda x: x["order_date"].dt.to_period("M"),
            amount_bucket=lambda x: pd.cut(x["amount"], bins=[0, 50, 200, 1000, float("inf")],
                                           labels=["small", "medium", "large", "enterprise"]),
        )
        .drop_duplicates(subset=["order_id"])
        .query("amount > 0")
    )

def load_to_postgres(df: pd.DataFrame, table: str, connection_string: str) -> None:
    """Load DataFrame to PostgreSQL with upsert."""
    from sqlalchemy import create_engine
    engine = create_engine(connection_string)
    df.to_sql(table, engine, if_exists="append", index=False, method="multi", chunksize=1000)
```

## Data Validation

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ValidationResult:
    passed: bool
    failures: list[str]

def validate_dataframe(df: pd.DataFrame) -> ValidationResult:
    """Run data quality checks on a DataFrame."""
    failures = []

    # Schema checks
    required_columns = {"id", "email", "amount", "created_at"}
    missing = required_columns - set(df.columns)
    if missing:
        failures.append(f"Missing columns: {missing}")

    # Null checks
    null_counts = df[["id", "email"]].isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            failures.append(f"Column '{col}' has {count} null values")

    # Range checks
    if (df["amount"] < 0).any():
        failures.append(f"Negative amounts found: {(df['amount'] < 0).sum()} rows")

    # Uniqueness checks
    dupes = df["id"].duplicated().sum()
    if dupes > 0:
        failures.append(f"Duplicate IDs found: {dupes}")

    # Freshness check
    max_date = df["created_at"].max()
    if pd.Timestamp.now() - max_date > pd.Timedelta(hours=24):
        failures.append(f"Data is stale: latest record is {max_date}")

    return ValidationResult(passed=len(failures) == 0, failures=failures)
```

## Kafka Streaming

```python
# Producer
from confluent_kafka import Producer
import json

producer = Producer({"bootstrap.servers": "localhost:9092"})

def publish_event(topic: str, key: str, data: dict) -> None:
    producer.produce(
        topic=topic,
        key=key.encode("utf-8"),
        value=json.dumps(data).encode("utf-8"),
        callback=lambda err, msg: print(f"Error: {err}") if err else None,
    )
    producer.flush()

# Consumer
from confluent_kafka import Consumer

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "etl-pipeline",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})
consumer.subscribe(["orders"])

def consume_and_process():
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        data = json.loads(msg.value().decode("utf-8"))
        process_order(data)
        consumer.commit(msg)
```

## dbt Transformations

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

SELECT
    id AS order_id,
    customer_id,
    CAST(amount AS DECIMAL(10, 2)) AS amount,
    status,
    created_at::timestamp AS ordered_at
FROM {{ source('raw', 'orders') }}
WHERE status != 'cancelled'

-- models/marts/fct_daily_revenue.sql
{{ config(materialized='table', partition_by={'field': 'order_date', 'data_type': 'date'}) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
daily AS (
    SELECT
        DATE_TRUNC('day', ordered_at) AS order_date,
        COUNT(*) AS total_orders,
        SUM(amount) AS total_revenue,
        AVG(amount) AS avg_order_value,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM orders
    GROUP BY 1
)
SELECT
    *,
    SUM(total_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7d_rolling
FROM daily

-- tests/assert_positive_revenue.sql
SELECT * FROM {{ ref('fct_daily_revenue') }} WHERE total_revenue < 0
```

```yaml
# dbt_project.yml
name: analytics
version: "1.0.0"
profile: default

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: analytics
```

## Pipeline Orchestration (Airflow-style DAG)

```python
# Using a simplified DAG pattern
from dataclasses import dataclass, field
from typing import Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Task:
    name: str
    fn: Callable
    depends_on: list[str] = field(default_factory=list)
    retries: int = 3

class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.tasks: dict[str, Task] = {}
        self.results: dict[str, Any] = {}

    def add_task(self, task: Task) -> None:
        self.tasks[task.name] = task

    def run(self) -> dict[str, Any]:
        executed = set()
        while len(executed) < len(self.tasks):
            for name, task in self.tasks.items():
                if name in executed:
                    continue
                if all(dep in executed for dep in task.depends_on):
                    logger.info(f"Running task: {name}")
                    for attempt in range(task.retries):
                        try:
                            self.results[name] = task.fn()
                            executed.add(name)
                            break
                        except Exception as e:
                            logger.error(f"Task {name} failed (attempt {attempt + 1}): {e}")
                            if attempt == task.retries - 1:
                                raise
        return self.results

# Usage
pipeline = Pipeline("daily_etl")
pipeline.add_task(Task("extract", extract_orders))
pipeline.add_task(Task("transform", transform_orders, depends_on=["extract"]))
pipeline.add_task(Task("validate", validate_data, depends_on=["transform"]))
pipeline.add_task(Task("load", load_to_warehouse, depends_on=["validate"]))
pipeline.run()
```

## Star Schema Design

```sql
-- Dimension tables
CREATE TABLE dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT,
    email TEXT,
    segment TEXT,
    -- SCD Type 2 fields
    valid_from TIMESTAMP DEFAULT NOW(),
    valid_to TIMESTAMP DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

-- Fact table
CREATE TABLE fct_orders (
    order_key SERIAL PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_key INT REFERENCES dim_customers(customer_key),
    product_key INT REFERENCES dim_products(product_key),
    date_key INT REFERENCES dim_dates(date_key),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0
);

-- Date dimension (generate once)
CREATE TABLE dim_dates AS
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d AS full_date,
    EXTRACT(YEAR FROM d) AS year,
    EXTRACT(QUARTER FROM d) AS quarter,
    EXTRACT(MONTH FROM d) AS month,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(DOW FROM d) AS day_of_week,
    TO_CHAR(d, 'Day') AS day_name,
    CASE WHEN EXTRACT(DOW FROM d) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day') AS d;
```

## Additional Resources

- dbt Documentation: https://docs.getdbt.com/
- Apache Kafka: https://kafka.apache.org/documentation/
- Apache Airflow: https://airflow.apache.org/docs/
- Great Expectations (data validation): https://docs.greatexpectations.io/
