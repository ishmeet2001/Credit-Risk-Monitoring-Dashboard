from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import psycopg2
from kafka import KafkaConsumer
from prometheus_client import start_http_server

from app.api.preprocess import preprocess_event, validate_required_features
from app.api.rules import apply_rules
from streaming.consumer_metrics import (
    CONSUMER_EVENTS_TOTAL,
    CONSUMER_PROCESSING_LATENCY,
    CONSUMER_LAST_EVENT_TS,
    CONSUMER_LAG_SECONDS,
)
from streaming.raw_event_sink import RawEventSink


KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "loan_applications")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB = os.getenv("PG_DB", "credit_risk")
PG_USER = os.getenv("PG_USER", "credit")
PG_PASSWORD = os.getenv("PG_PASSWORD", "risk")


def pg_connect():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )


INSERT_SQL = """
INSERT INTO risk_scored (
  loan_id, purpose, term,
  loan_amnt, annual_inc, dti, int_rate_pct, revol_util_pct,
  delinq_2yrs, inq_last_6mths, credit_history_years, emp_length_yrs,
  dti_band, util_band, rate_band,
  early_warning_flag, risk_tier, reasons
) VALUES (
  %(loan_id)s, %(purpose)s, %(term)s,
  %(loan_amnt)s, %(annual_inc)s, %(dti)s, %(int_rate_pct)s, %(revol_util_pct)s,
  %(delinq_2yrs)s, %(inq_last_6mths)s, %(credit_history_years)s, %(emp_length_yrs)s,
  %(dti_band)s, %(util_band)s, %(rate_band)s,
  %(early_warning_flag)s, %(risk_tier)s, %(reasons)s
);
"""


def normalize_event_id(event: Dict[str, Any]) -> str:
    """
    Choose a stable ID for storage. Your producer may send 'id' or 'loan_id' or neither.
    """
    if event.get("loan_id") is not None:
        return str(event["loan_id"])
    if event.get("id") is not None:
        return str(event["id"])
    # fallback: not ideal, but prevents null key inserts
    return f"evt_{int(time.time() * 1000)}"


def main():
    # Expose metrics on http://localhost:9101/metrics
    print("Starting Prometheus metrics server on port 9101...")
    start_http_server(9101)

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="credit-risk-consumer-v1",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=1000,  # lets us print heartbeat if idle
    )

    conn = pg_connect()
    conn.autocommit = False
    cur = conn.cursor()

    processed = 0
    skipped = 0
    last_log = time.time()

    print(f"✅ Consumer connected. Topic='{KAFKA_TOPIC}' bootstrap='{KAFKA_BOOTSTRAP}'")
    print(f"✅ Postgres connected. db='{PG_DB}' host='{PG_HOST}:{PG_PORT}' user='{PG_USER}'")

    # Raw Event Sink Setup
    raw_enabled = os.getenv("RAW_EVENTS_TO_S3", "false").lower() == "true"
    raw_prefix = os.getenv("RAW_EVENTS_PREFIX", "raw_events")
    raw_flush = int(os.getenv("RAW_EVENTS_FLUSH_EVERY", "500"))
    raw_dir = os.getenv("RAW_EVENTS_LOCAL_DIR", "tmp/raw_events")

    raw_sink = RawEventSink(
        enabled=raw_enabled,
        s3_prefix=raw_prefix,
        flush_every=raw_flush,
        local_dir=raw_dir,
    )

    try:
        while True:
            got_any = False
            for msg in consumer:
                t0 = time.time()
                got_any = True
                event = msg.value  # dict
                
                # Archive raw event
                raw_sink.append(event)
                
                loan_id = normalize_event_id(event)

                features = preprocess_event(event)
                ok, missing = validate_required_features(features)
                if not ok:
                    skipped += 1
                    CONSUMER_EVENTS_TOTAL.labels(status="skipped").inc()
                    CONSUMER_PROCESSING_LATENCY.observe(time.time() - t0)
                    continue

                decision = apply_rules(features)

                # Prepare row and convert numpy types to native Python types
                row = {
                    "loan_id": loan_id,
                    "purpose": features.get("purpose"),
                    "term": features.get("term"),
                    "loan_amnt": float(features.get("loan_amnt")) if pd.notna(features.get("loan_amnt")) else None,
                    "annual_inc": float(features.get("annual_inc")) if pd.notna(features.get("annual_inc")) else None,
                    "dti": float(features.get("dti")) if pd.notna(features.get("dti")) else None,
                    "int_rate_pct": float(features.get("int_rate_pct")) if pd.notna(features.get("int_rate_pct")) else None,
                    "revol_util_pct": float(features.get("revol_util_pct")) if pd.notna(features.get("revol_util_pct")) else None,
                    "delinq_2yrs": int(features.get("delinq_2yrs")) if pd.notna(features.get("delinq_2yrs")) else None,
                    "inq_last_6mths": int(features.get("inq_last_6mths")) if pd.notna(features.get("inq_last_6mths")) else None,
                    "credit_history_years": float(features.get("credit_history_years")) if pd.notna(features.get("credit_history_years")) else None,
                    "emp_length_yrs": float(features.get("emp_length_yrs")) if pd.notna(features.get("emp_length_yrs")) else None,
                    "dti_band": decision.get("dti_band"),
                    "util_band": decision.get("util_band"),
                    "rate_band": decision.get("rate_band"),
                    "early_warning_flag": decision.get("early_warning_flag"),
                    "risk_tier": decision.get("risk_tier"),
                    "reasons": ",".join(decision.get("reasons", [])),
                }

                try:
                    cur.execute(INSERT_SQL, row)
                    processed += 1

                    # commit in batches for speed
                    if processed % 200 == 0:
                        conn.commit()
                    
                    CONSUMER_EVENTS_TOTAL.labels(status="ok").inc()
                    CONSUMER_LAST_EVENT_TS.set(time.time())

                except Exception as e:
                    conn.rollback()
                    skipped += 1
                    # keep going; streaming should be resilient
                    print(f"⚠️ Insert failed for loan_id={loan_id}: {e}")
                    CONSUMER_EVENTS_TOTAL.labels(status="db_error").inc()
                finally:
                    CONSUMER_PROCESSING_LATENCY.observe(time.time() - t0)
                    if msg.timestamp:
                        lag = time.time() - (msg.timestamp / 1000.0)
                        CONSUMER_LAG_SECONDS.set(lag)

                # periodic log
                now = time.time()
                if now - last_log > 3:
                    print(f"📥 processed={processed} skipped={skipped}")
                    last_log = now

            # if we timed out (no messages), commit any pending and keep looping
            if not got_any:
                if processed % 200 != 0:
                    conn.commit()
                time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n Stopping consumer...")
    finally:
        try:
            conn.commit()
        except Exception:
            pass
        raw_sink.close()
        cur.close()
        conn.close()
        consumer.close()
        print(f" Final: processed={processed} skipped={skipped}")


if __name__ == "__main__":
    main()
