from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "credit_risk_requests_total",
    "Total scoring requests",
    ["endpoint", "status"],
)

SCORING_LATENCY = Histogram(
    "credit_risk_scoring_latency_seconds",
    "Latency for scoring requests",
    ["endpoint"],
)

WATCHLIST_TOTAL = Counter(
    "credit_risk_watchlist_total",
    "Total watchlist decisions",
    ["source"],
)
