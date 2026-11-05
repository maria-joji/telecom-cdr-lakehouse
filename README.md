# Telecom CDR Lakehouse

> One paragraph: what problem this solves and for whom. Write this last, in your own words.

## Architecture

(Add a diagram here: landing -> bronze -> silver -> gold, plus control tables.)

## What it does
- Ingests daily call detail record (CDR) and customer snapshot files
- Cleans, validates and deduplicates records, with a quarantine table for bad rows
- Keeps customer history with SCD Type 2
- Records every file and run in audit tables and reconciles counts between layers

## Tech
Databricks, PySpark, Delta Lake, Spark SQL, Python, GitHub Actions, pytest

## Data
Synthetic data from `src/generate_cdr.py`, with deliberate problems (duplicates, bad rows,
late records, changing customers). See `docs/design.md`.

## How to run
1. `python src/generate_cdr.py --days 7 --rows 20000 --out data`
2. Upload `data/` to your workspace
3. Run the notebooks in order: 01_bronze, 02_silver, 03_gold_scd2

## Results
(Add real numbers from your own run: rows loaded, duplicates removed, rows quarantined,
customers with changed history.)

## What I would add next
(Streaming ingestion, dbt models, a RAG layer over support text.)
