# Databricks notebook source
# SILVER: type, validate, deduplicate
#
# TODO 1  Read only the rows of bronze_cdr that are not yet in silver (by run_id or ingest_ts)
# TODO 2  Cast columns to the right types
# TODO 3  Apply the validation rules from docs/design.md and send failures to quarantine_cdr
# TODO 4  Deduplicate on call_id (ROW_NUMBER, keep the latest ingest_ts)
# TODO 5  MERGE into silver_cdr on call_id
# TODO 6  Reconciliation: bronze rows = silver rows + quarantined + duplicates removed
