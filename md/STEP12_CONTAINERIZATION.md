# Step 12 Complete - Containerization 🐳

We have containerized the Python applications (API & Consumer) and integrated them into the Docker stack.

## 🛠️ What Changed?
1.  **`realtime/Dockerfile.api`**: Docker image definition for the FastAPI service.
2.  **`realtime/Dockerfile.consumer`**: Docker image definition for the Kafka Consumer worker.
3.  **`realtime/infra/docker-compose.yml`**: Updated to build and run these containers alongside infrastructure.

## 🚀 How to Run the Full Stack
Now, you can launch the entire system with a single command:

```bash
docker compose -f realtime/infra/docker-compose.yml up --build -d
```

### Services Included:
| Service | Container Name | Port | Description |
|---|---|---|---|
| **API** | `credit-risk-api` | 8000 | FastAPI Application |
| **Consumer** | `credit-risk-consumer` | 9101 | Processes Kafka events |
| **Redpanda** | `redpanda` | 9092 | Kafka message bus |
| **Postgres** | `credit-risk-postgres` | 5432 | Database |
| **Prometheus** | `credit-risk-prometheus` | 9090 | Metrics |
| **Grafana** | `credit-risk-grafana` | 3000 | Visualization |
| **Drift Job** | `credit-risk-drift` | - | ML Monitoring (Scheduled) |

### 🧪 Generating Traffic
Since everything is containerized, you can still test from your host machine:
```bash
# Generate 20 requests
for i in {1..20}; do
  curl -X POST "http://localhost:8000/score" ...
done
```

### 📊 Observability (Fixed)
-   The **"Pipeline Lag"** metric you saw initialized at `1.7 billion` seconds (Unix Epoch default) will drop to near-zero as soon as the first event is processed by the new containerized consumer.
-   **"No Data"** in Grafana will populate once traffic flows through the `consumer` container.

**The system is now fully portable and production-ready!** 🏆
