# Design: telecom CDR lakehouse

## 1. Data flow

    daily files (cdr_YYYYMMDD.csv, customers_YYYYMMDD.csv)
        -> landing folder
        -> BRONZE  (raw, as-is, plus audit columns)
        -> SILVER  (typed, deduplicated, validated; bad rows to quarantine)
        -> GOLD    (dim_customer as SCD Type 2, fact_usage_daily)
    control tables record every file, run, count and error

## 2. Source files

cdr_YYYYMMDD.csv
call_id, customer_id, callee_number, call_type (VOICE/SMS/DATA), start_time,
duration_sec, data_mb, tower_id, status (COMPLETED/DROPPED/FAILED)

customers_YYYYMMDD.csv  (full snapshot every day)
customer_id, plan, city, segment, active_flag

Known problems in the data (by design): duplicate call_id, null customer_id,
negative duration, records that belong to the previous day, customers that change plan or city.

## 3. Bronze

| Table | Content |
|---|---|
| bronze_cdr | all source columns read as STRING, plus file_name, ingest_ts, run_id |
| bronze_customers | same idea for the customer snapshot |

Rules
- Read everything as string, so no row is lost to a bad type.
- Load is safe to rerun: delete rows for the same file_name, then append.

## 4. Silver

| Table | Content |
|---|---|
| silver_cdr | typed columns, one row per call_id, only valid rows |
| quarantine_cdr | rejected rows with a reject_reason column |

Rules (write each as a function you can test)
1. customer_id must not be null  -> else quarantine, reason NULL_CUSTOMER
2. duration_sec must be >= 0     -> else quarantine, reason NEGATIVE_DURATION
3. start_time must parse to a timestamp -> else quarantine, reason BAD_TIMESTAMP
4. duplicates: keep one row per call_id (latest ingest_ts)
5. load into silver with MERGE on call_id, so a late or repeated file updates, not duplicates

## 5. Gold

dim_customer (SCD Type 2)
customer_sk, customer_id, plan, city, segment, checksum, is_active, start_date, end_date
- checksum = hash of plan, city, segment
- changed checksum -> close the old row, insert the new version

fact_usage_daily
customer_id, usage_date, calls, call_minutes, sms_count, data_mb, dropped_calls
- recomputed for every date touched by a load (this handles late-arriving records)

## 6. Control tables (Delta now, Azure SQL if you later move them)

file_audit    : file_name, source_name, row_count_in_file, received_ts, status
process_audit : run_id, layer, start_ts, end_ts, status, rows_read, rows_written
recon_audit   : run_id, layer, source_count, target_count, rejected_count, match_flag
error_log     : run_id, file_name, layer, error_message, logged_ts

Reconciliation rule per file:
rows in file = rows in bronze;  rows in bronze = silver rows + quarantined rows + duplicates removed

## 7. Open questions to decide while building
- How do you partition silver_cdr (by start_date is a good first choice)?
- What threshold of bad rows should stop a load instead of continuing?
- How will you alert on failure?
