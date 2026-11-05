# Databricks notebook source
# BRONZE: load raw files, as-is, with audit columns
#
# TODO 1  Read config/sources.json (or a config Delta table) and loop over active sources
# TODO 2  Read one CDR file with header=True and every column as string (no inferSchema)
# TODO 3  Add file_name (hint: _metadata.file_name), ingest_ts and run_id
# TODO 4  Make it rerun-safe: delete existing rows for this file_name, then append
# TODO 5  Write a row to file_audit and process_audit
# TODO 6  Check: row count in file = row count loaded; write recon_audit
