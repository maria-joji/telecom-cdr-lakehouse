# Plan (starts Mon 16 Nov 2026)

Daily rhythm: project work about 3 to 4 hours, outreach 30 to 45 minutes, one SQL or PySpark question.

| Dates | Phase | Deliverable |
|---|---|---|
| 16 to 22 Nov | 1. Setup and bronze | repo on GitHub, data generated, bronze load with audit columns, rerun-safe, README draft |
| 23 to 29 Nov | 2. Silver and quality | validation rules, quarantine table, dedup, MERGE, audit and recon tables |
| 30 Nov to 6 Dec | 3. Gold and history | SCD2 dim_customer, fact_usage_daily, OPTIMIZE, late data handled |
| 7 to 13 Dec | 4. Automation | Databricks Job or Workflow, pytest tests, GitHub Actions |
| 14 to 20 Dec | 5. Streaming basics | Auto Loader or Structured Streaming on bronze |
| 21 Dec to 10 Jan | 6. AI layer | RAG pipeline: chunk, embed, vector index, answers with sources, simple evaluation |
| 11 Jan to 31 Jan | 7. Breadth | dbt models, an Airflow DAG, Fabric and Synapse concepts, Docker basics |
| Feb | 8. Polish | clean READMEs, diagrams, 2 short write-ups, mock interviews |
| Mar | Buffer | interviews, final fixes |

Checkpoint every Sunday: what is done, what is blocked, what changes.
