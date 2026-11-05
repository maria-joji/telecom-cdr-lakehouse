# Databricks notebook source
# GOLD: dim_customer (SCD Type 2) and fact_usage_daily
#
# TODO 1  Read today's customer snapshot, add checksum, is_active, start_date, end_date
# TODO 2  MERGE: close the changed rows
# TODO 3  Insert the new versions of the changed customers (and new customers)
# TODO 4  Build fact_usage_daily for every usage_date touched by the load
# TODO 5  OPTIMIZE the tables you read most
# TODO 6  Test it: change one customer's plan in a new snapshot and check the history
