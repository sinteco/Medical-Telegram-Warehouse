# Medical Telegram Warehouse - Task 2: Data Warehouse

This branch focuses on the **Data Warehouse** layer using **dbt (data build tool)**. It transforms raw data ingested from Telegram into analytical models.

## Project Structure

- `medical_warehouse/`: Main dbt project directory.
    - `models/staging/`: Raw data cleaning and standardization.
    - `models/marts/`: Business-logic data marts (Fact and Dimension tables).
    - `tests/`: Data quality tests (schema and custom tests).
    - `seeds/`: Static reference data (if any).

## Data Flow

1.  **Raw Data**: Sourced from PostgreSQL `raw` schema (populated by Task 1 ingestion scripts).
2.  **Staging (`stg_telegram`)**:
    - Cleans raw text.
    - Extracts metadata (message length, media flags).
    - Deduplicates based on `channel_name` and `message_id`.
3.  **Marts**:
    - `dim_channels`: Unique list of telegram channels.
    - `dim_dates`: Date dimension for time-series analysis.
    - `fct_messages`: Fact table containing message metrics (views, forwards) linked to dimensions.

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL
- dbt-core & dbt-postgres

### Setup

1.  Navigate to the dbt project folder:
    ```bash
    cd medical_warehouse
    ```

2.  Install dbt dependencies:
    ```bash
    dbt deps
    ```

3.  Configure your `profiles.yml` (usually in `~/.dbt/`) or use the project local one if configured.

### Running Models

Run all models:
```bash
dbt run
```

Run specific model:
```bash
dbt run --select fct_messages
```

### Testing

Run data quality tests:
```bash
dbt test
```
