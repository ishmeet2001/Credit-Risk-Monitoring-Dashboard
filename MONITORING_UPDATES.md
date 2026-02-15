# Kafka Consumer Pipeline & Monitoring Updates

This document summarizes the instrumentation and monitoring enhancements implemented to ensure high reliability and observability for the Credit Risk Early Warning system.

## 1. Consumer Pipeline Instrumentation
The Kafka consumer has been instrumented with **Prometheus** metrics to track throughput, latency, and system health.

- **File**: `realtime/streaming/consumer.py`, `realtime/streaming/consumer_metrics.py`
- **New Metrics Exposed (Port 9101)**:
    - `credit_risk_consumer_events_total`: Counter tracking events with statuses: `ok` (successful DB insert), `skipped` (validation failed), and `db_error` (database insertion failure).
    - `credit_risk_consumer_processing_latency_seconds`: Histogram measuring the full cycle from ingestion to DB commit.
    - `credit_risk_consumer_lag_seconds`: Gauge measuring the **End-to-End Lag** (current time minus the original Kafka message creation timestamp).
    - `credit_risk_consumer_last_event_unixtime`: Gauge acting as a "Last Pulse" heartbeat for the consumer.

- **System Fixes**:
    - Resolved `ModuleNotFoundError` for the `app` package by correcting `PYTHONPATH` in `Dockerfile.consumer`.
    - Fixed `NameError` for `pd.notna` in the consumer loop.
    - Added explicit type casting for `numpy` types to satisfy PostgreSQL adaptation requirements during insertion.

## 2. Infrastructure & Networking
Enhanced the Docker service definitions for better inter-service reliability.

- **Redpanda Connectivity**: Updated services (`api`, `consumer`, `drift-job`) to use the internal Docker network port `redpanda:29092` for Kafka operations, reducing external host dependencies.
- **Drift Job Environment**: Updated `drift-job` service in `docker-compose.yml` to:
    - Include `boto3` for AWS S3 integration.
    - Mount the root `.env` file via `env_file` to provide AWS credentials dynamically.
    - Set correct `PYTHONPATH` to leverage shared utility functions.

## 3. Persistent Drift Analysis
The periodic drift detection system is now automated and persists its results.

- **File**: `monitoring/drift_job.py`
- **Persistence**: Reports are now automatically uploaded to the **S3 Bucket** (`credit-risk-lake`) after local generation. 
    - Keys are timestamped: `reports/drift/drift_report_YYYYMMDD_HHMMSS.html`.
- **Compatibility**: Logic updated to align with `Evidently 0.4.x` API patterns found in the container image.

## 4. Enhanced Dashboards & Alerting
The monitoring GUI and automated alerting system have been upgraded to provide proactive failure detection.

### Grafana Dashboard Improvements
- **Location**: `realtime/infra/grafana/dashboards/credit_risk_dashboard.json`
- **New Panels**:
    - **E2E Lag (ms)**: Visualizes real-time pipeline delay.
    - **Liveness Lag (sec)**: Detects if the consumer service has crashed or stopped pulling messages.
    - **Consumer Latency P95 (ms)**: Tracks the time taken to process and store loan events.

### Alerting Rules
- **Location**: `realtime/infra/alerts.yml`
- **New Alerts**:
    - `HighConsumerLag`: Triggers if the pipeline is >5 seconds behind for more than 2 minutes.
    - `HighConsumerErrorRate`: Triggers if more than 5% of messages fail database insertion over a 2-minute window (Severty: `page`).

---
*Created on: 2026-02-14*
