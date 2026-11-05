"""
Synthetic telecom data generator for the CDR lakehouse project.

Creates, in the output folder:
  cdr/cdr_YYYYMMDD.csv           one call detail record file per day
  customers/customers_YYYYMMDD.csv   a full customer snapshot per day (for SCD Type 2)

Deliberate data problems (so the pipeline has something to catch):
  - about 1% duplicate records (same call_id appears twice)
  - about 0.5% bad records (null customer_id or negative duration)
  - about 1% late-arriving records (start_time belongs to the previous day)
  - about 2% of customers change plan or city on each day after the first

Usage:
  python generate_cdr.py --days 7 --rows 20000 --out data
"""
import argparse
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

PLANS = ["Prepaid-199", "Prepaid-299", "Postpaid-499", "Postpaid-799", "Postpaid-999"]
CITIES = ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata", "Kochi"]
CALL_TYPES = ["VOICE", "SMS", "DATA"]
CALL_TYPE_WEIGHTS = [0.55, 0.25, 0.20]
STATUSES = ["COMPLETED", "DROPPED", "FAILED"]
STATUS_WEIGHTS = [0.93, 0.05, 0.02]


def make_customers(n, rng):
    return pd.DataFrame({
        "customer_id": [f"CUST{i:06d}" for i in range(1, n + 1)],
        "plan": rng.choice(PLANS, n),
        "city": rng.choice(CITIES, n),
        "segment": rng.choice(["CONSUMER", "SMB", "ENTERPRISE"], n, p=[0.8, 0.15, 0.05]),
        "active_flag": 1,
    })


def evolve_customers(df, rng, change_rate=0.02):
    df = df.copy()
    idx = rng.choice(df.index, int(len(df) * change_rate), replace=False)
    for i in idx:
        if rng.random() < 0.5:
            df.at[i, "plan"] = rng.choice(PLANS)
        else:
            df.at[i, "city"] = rng.choice(CITIES)
    return df


def make_cdr_day(day, rows, customers, rng, seq_start):
    ids = [f"CDR{day:%Y%m%d}{seq_start + i:07d}" for i in range(rows)]
    call_type = rng.choice(CALL_TYPES, rows, p=CALL_TYPE_WEIGHTS)

    start = pd.Timestamp(day) + pd.to_timedelta(rng.integers(0, 86400, rows), unit="s")

    duration = np.where(call_type == "VOICE", rng.integers(5, 1800, rows), 0)
    data_mb = np.where(call_type == "DATA", np.round(rng.gamma(2.0, 40.0, rows), 2), 0.0)

    df = pd.DataFrame({
        "call_id": ids,
        "customer_id": rng.choice(customers["customer_id"].values, rows),
        "callee_number": [f"9{rng.integers(100000000, 999999999)}" for _ in range(rows)],
        "call_type": call_type,
        "start_time": start,
        "duration_sec": duration,
        "data_mb": data_mb,
        "tower_id": [f"T{rng.integers(1, 201):03d}" for _ in range(rows)],
        "status": rng.choice(STATUSES, rows, p=STATUS_WEIGHTS),
    })

    # late-arriving: about 1% of rows belong to the previous day
    late = rng.choice(df.index, max(1, rows // 100), replace=False)
    df.loc[late, "start_time"] = df.loc[late, "start_time"] - pd.Timedelta(days=1)

    # bad records: about 0.5%
    bad = rng.choice(df.index, max(1, rows // 200), replace=False)
    half = len(bad) // 2
    df.loc[bad[:half], "customer_id"] = None
    df.loc[bad[half:], "duration_sec"] = -1 * rng.integers(1, 100, len(bad) - half)

    # duplicates: about 1% of rows repeated
    dups = df.sample(max(1, rows // 100), random_state=int(rng.integers(0, 10**6)))
    df = pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=1).reset_index(drop=True)
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--rows", type=int, default=20000, help="records per day before duplicates")
    p.add_argument("--customers", type=int, default=5000)
    p.add_argument("--start", default="2026-10-01", help="first day, YYYY-MM-DD")
    p.add_argument("--out", default="data")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()

    rng = np.random.default_rng(a.seed)
    random.seed(a.seed)
    os.makedirs(os.path.join(a.out, "cdr"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "customers"), exist_ok=True)

    first = datetime.strptime(a.start, "%Y-%m-%d")
    customers = make_customers(a.customers, rng)

    for d in range(a.days):
        day = first + timedelta(days=d)
        if d > 0:
            customers = evolve_customers(customers, rng)
        tag = f"{day:%Y%m%d}"

        cust_path = os.path.join(a.out, "customers", f"customers_{tag}.csv")
        customers.to_csv(cust_path, index=False)

        cdr = make_cdr_day(day, a.rows, customers, rng, seq_start=1)
        cdr_path = os.path.join(a.out, "cdr", f"cdr_{tag}.csv")
        cdr.to_csv(cdr_path, index=False)
        print(f"{tag}: cdr rows={len(cdr):,}  customers={len(customers):,}")

    print(f"done, files written under {a.out}/")


if __name__ == "__main__":
    main()
