# 🚀 Real-Time Credit Risk Monitoring Platform

A production-style, end-to-end credit risk monitoring system that processes streaming loan events, applies real-time scoring, and delivers live dashboards with full observability and drift monitoring.

This project transforms raw LendingClub accepted-loan data into a governed, explainable early-warning view—combining batch ML modeling with a high-performance streaming pipeline.

---

## 🚀 Key Capabilities

### 🔹 Real-Time Streaming & Observability
*   **Kafka-compatible streaming (Redpanda)** for high-throughput event ingestion.
*   **Python Consumer** for real-time preprocessing, deterministic scoring, and S3 archiving.
*   **FastAPI-based Scoring API** with rule-based categorization and validation.
*   **Full Observability Stack**: Prometheus metrics (latency, throughput, lag) and Grafana.
*   **Data Lake Integration**: Automated archival of raw events and drift reports to **AWS S3**.

### 🔹 Risk Modeling & Analytics
*   **Standardized Preprocessing**: reproducible cleaning for DTI, utilization, and credit history.
*   **Rule-Based Risk Segmentation**: Interpretable banding to flag high-risk borrowers.
*   **ML Lift Validation**: Logistic Regression baseline model providing predictive lift (**AUC ≈ 0.69**).
*   **Drift Detection**: Automated monitoring using **Evidently** to ensure model reliability.

---

## 🏗️ Architecture

![Architecture Diagram](architecture_diagram_standard.png)

The system follows a modern "Medallion-style" architecture:
- **Silver Layer**: Scored events stored in **PostgreSQL** for real-time dashboarding.
- **Gold Layer**: Aggregated drift reports and raw event backups archived in **AWS S3**.

---

## 📊 System Preview

### Real-Time Engineering Monitoring (Grafana)
![Grafana Dashboard](dashboard_screenshot_v3.png)
*Track system health, consumer lag, and processing bottlenecks at a glance.*

### Business Risk Analytics (Streamlit)
![Streamlit Dashboard](business_dashboard_v2.png)
*Visualize risk distributions, watchlist volume, and high-risk borrower profiles.*

---

## ⚙️ Quickstart (Local)

### Prerequisites
*   Docker & Docker Desktop
*   Python 3.11+
*   AWS Account (for S3 Archival)

### 1. Setup Environment
```bash
cp .env.example .env  # Add your AWS credentials and PG settings
pip install -r requirements.txt
```

### 2. Start Infrastructure
```bash
cd realtime/infra
docker compose up -d --build
```

### 3. Generate Streaming Data
```bash
# Simulates real-time loan applications
export PYTHONPATH=$PYTHONPATH:$(pwd)/realtime
python realtime/streaming/producer.py --rate 10 --max 1000
```

### 🔗 Access Points
*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Grafana**: [http://localhost:3000](http://localhost:3000) (admin/admin)
*   **Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **Kafka Console**: [http://localhost:8080](http://localhost:8080)

---

## 🛠️ Tech Stack
*   **Streaming**: Kafka / Redpanda
*   **API**: FastAPI
*   **Database**: PostgreSQL
*   **Dashboard**: Streamlit
*   **Monitoring**: Prometheus, Grafana
*   **Drift Detection**: Evidently
*   **Cloud Storage**: AWS S3
*   **Infrastructure**: Docker

---

## 📂 Repository Structure
```text
├─ realtime/           # Real-time streaming services
│  ├─ app/api/         # Scoring API (FastAPI)
│  ├─ streaming/       # Kafka Consumer & Producer
│  ├─ dashboard/       # Streamlit Analytics
│  └─ infra/           # Docker Compose & Monitoring stack
├─ monitoring/         # Drift detection & ML monitoring jobs
├─ scripts/            # Pre-processing & rule-generation scripts
├─ analysis/           # Offline ML modeling & ROC evaluations
├─ data/               # Local data samples (Git ignored)
└─ .env                # Secrets and S3 configuration
```

---

## 🧠 Design Highlights
*   **Event-Driven Architecture**: High-efficiency real-time processing using Kafka.
*   **Observability-First**: Built-in metrics and alerts from the ground up.
*   **Hybrid Storage**: Separation of serving layer (Postgres) and data lake (S3).
*   **Reproducible**: Fully Dockerized environment for one-command deployment.
