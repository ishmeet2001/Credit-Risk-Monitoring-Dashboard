from prometheus_client import Counter, Histogram, Gauge

CONSUMER_EVENTS_TOTAL = Counter(
    "credit_risk_consumer_events_total",
    "Kafka events consumed",
    ["status"],  # ok, skipped, db_error
)

CONSUMER_PROCESSING_LATENCY = Histogram(
    "credit_risk_consumer_processing_latency_seconds",
    "Time to preprocess + rules + DB insert",
)

CONSUMER_LAST_EVENT_TS = Gauge(
    "credit_risk_consumer_last_event_unixtime",
    "Unix timestamp of last processed event",
)

CONSUMER_LAG_SECONDS = Gauge(
    "credit_risk_consumer_lag_seconds",
    "End-to-end lag (processing time - kafka timestamp)",
)
