# 🚀 Project Complete: Real-Time Credit Risk Monitoring System

The system is fully deployed and operational. Here is your access guide.

## 📊 Dashboard Access (Grafana)
- **URL**: [http://localhost:3000](http://localhost:3000)
- **Direct Dashboard Link**: [Credit Risk Monitoring (Real-Time)](http://localhost:3000/d/credit-risk-rt/credit-risk-monitoring-real-time)
- **Credentials**:
  - **Username**: `admin`
  - **Password**: `admin`
  - *(Skip password change on first login)*

## 🔬 Observability Stack
| Component | URL | Description |
|---|---|---|
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | Metrics collection & query |
| **Alertmanager** | [http://localhost:9093](http://localhost:9093) | Alert routing & status |
| **Drift Reports** | `monitoring/reports/drift_report.html` | Open directly in browser |

## 🕹️ Application Interfaces
| Component | URL | Description |
|---|---|---|
| **Streamlit Dashboard** | [http://localhost:8501](http://localhost:8501) | Real-time business dashboard |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API documentation |

## 🏗️ Infrastructure Service Status
| Service | Status | Port |
|---|---|---|
| `redpanda` | ✅ Running | 9092, 8081 |
| `kafka-console` | ✅ Running | 8080 |
| `postgres` | ✅ Running | 5433 |
| `grafana` | ✅ Running | 3000 |
| `drift-job` | ✅ Running | Dockerized |

## 🧪 Simulation
To generate more traffic and see the dashboard light up:
```bash
# Run this loop to send 50 scoring requests to the API
for i in {1..50}; do
  curl -s -X POST "http://localhost:8000/score" \
    -H "Content-Type: application/json" \
    -d '{ "persist_to_db": false, "event": { "loan_id": "sim_'"$i"'", "loan_amnt": 12000, "dti": 33.2 } }' > /dev/null
done
```

**Congratulations! You have built a production-grade, observable, and scalable ML system.** 🏆
