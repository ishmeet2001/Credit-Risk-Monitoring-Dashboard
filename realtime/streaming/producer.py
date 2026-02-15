# streaming/producer.py
from __future__ import annotations

import json
import time
import argparse
from typing import Optional

import pandas as pd
from kafka import KafkaProducer


def build_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: (k.encode("utf-8") if isinstance(k, str) else k),
        acks="all",
        linger_ms=10,
        retries=5,
    )


def main():
    parser = argparse.ArgumentParser(description="Replay LendingClub rows into Kafka as JSON events.")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", default="loan_applications", help="Kafka topic name")
    parser.add_argument("--csv", default="data/processed/sample_100k.csv", help="Path to input CSV")
    parser.add_argument("--rate", type=float, default=10.0, help="Events per second (approx)")
    parser.add_argument("--max", type=int, default=0, help="Max events to send (0 = all)")
    parser.add_argument("--sleep", type=float, default=0.0, help="Extra sleep per event (seconds)")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    # Make sure there is some stable ID. If your CSV doesn't have id, we create one.
    if "id" not in df.columns and "loan_id" not in df.columns:
        df["loan_id"] = [f"loan_{i}" for i in range(len(df))]
        id_col = "loan_id"
    else:
        id_col = "id" if "id" in df.columns else "loan_id"

    producer = build_producer(args.bootstrap)

    # pacing
    per_event_delay = 1.0 / args.rate if args.rate > 0 else 0.0

    sent = 0
    started = time.time()

    for _, row in df.iterrows():
        event = row.to_dict()

        # Normalize NaNs to None so JSON is clean
        for k, v in list(event.items()):
            if pd.isna(v):
                event[k] = None

        # add event_time for monitoring + ordering
        event["event_time"] = pd.Timestamp.utcnow().isoformat()

        key = str(event.get(id_col, ""))

        producer.send(args.topic, key=key, value=event)
        sent += 1

        # flush periodically for demo stability
        if sent % 200 == 0:
            producer.flush()

        if args.sleep > 0:
            time.sleep(args.sleep)
        elif per_event_delay > 0:
            time.sleep(per_event_delay)

        if args.max and sent >= args.max:
            break

    producer.flush()
    elapsed = time.time() - started
    print(f"✅ Sent {sent} events to topic '{args.topic}' in {elapsed:.2f}s (~{sent/elapsed:.1f} eps)")

    producer.close()


if __name__ == "__main__":
    main()
