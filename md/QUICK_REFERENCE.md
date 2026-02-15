# Real-Time Credit Risk System - Quick Reference

**Branch**: `realtime-v1` | **Status**: ✅ Ready for Streaming

---

## 🎯 What We Built

Transformed batch CSV processing → Real-time event processing system

---

## 📦 Components

### 1. Event Processing Functions
- **`preprocess_event()`** - Transform raw events → features
- **`validate_required_features()`** - Check for missing fields
- **`apply_rules()`** - Apply risk assessment logic

### 2. Docker Infrastructure
- **Redpanda** (Kafka) - Message broker on port 9092
- **Redpanda Console** - Web UI on http://localhost:8080
- **PostgreSQL** - Database on port 5433

---

## 🚀 Quick Start

### Run Tests
```bash
cd realtime/app
python test_updated.py
```

### Start Infrastructure
```bash
docker compose -f realtime/infra/docker-compose.yml up -d
```

### Check Services
```bash
docker ps
docker exec -it redpanda rpk cluster info
docker exec -it credit-risk-postgres pg_isready -U credit -d credit_risk
```

### View Kafka UI
Open: http://localhost:8080

### Start Dashboard
```bash
streamlit run realtime/dashboard/streamlit_app.py
```
Open: http://localhost:8501

### Start API
```bash
cd realtime
uvicorn app.api.main:app --reload --port 8000
```
Open: http://localhost:8000/docs

### View Prometheus
Open: http://localhost:9090

---

## 💻 Code Example

```python
from api.preprocess import preprocess_event, validate_required_features
from api.rules import apply_rules

# Raw loan application
event = {
    "loan_amnt": 12000,
    "int_rate": "21.5%",
    "dti": 33.2,
    "revol_util": "85%",
    "delinq_2yrs": 1,
    "inq_last_6mths": 2,
    "emp_length": "3 years",
    "earliest_cr_line": "2012-05-01",
    ...
}

# Process
features = preprocess_event(event)
ok, missing = validate_required_features(features)

if ok:
    decision = apply_rules(features)
    print(decision)
    # {
    #   "risk_tier": "Watchlist",
    #   "early_warning_flag": 1,
    #   "reasons": ["DTI>=30", "REVOL_UTIL>=80", ...]
    # }
```

---

## 📁 Key Files

```
realtime/
├── app/api/
│   ├── preprocess.py       # Event preprocessing
│   ├── rules.py            # Risk assessment
│   └── __init__.py
├── app/test_updated.py     # Test suite
└── infra/
    └── docker-compose.yml  # Infrastructure
```

---

## 🔗 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Redpanda Console | http://localhost:8080 | View topics/messages |
| Kafka API | localhost:9092 | Produce/consume |
| PostgreSQL | localhost:5433 | Database |

**PostgreSQL Connection**:
```
postgresql://credit:risk@localhost:5433/credit_risk
```

---

## 📊 Stats

- **Code Reduction**: 48% (399 → 209 lines)
- **Test Coverage**: 5/5 passing
- **Services Running**: 3/3 healthy
- **Documentation**: 4 comprehensive docs

---

## 🎯 Next Steps

1. Create Kafka topics (`loan-applications`, `scored-loans`)
2. Build Kafka producer (read CSV → publish events)
3. Build Kafka consumer (subscribe → process → store)
4. Create FastAPI endpoints for real-time scoring
5. Build real-time dashboard

---

## 📚 Full Documentation

- **CHANGELOG.md** - Complete change history
- **STEP1_IMPROVEMENTS.md** - Code improvements
- **STEP2B_DOCKER_STACK.md** - Docker setup
- **STEP1_SUMMARY.md** - Initial refactoring

---

## 🐛 Troubleshooting

**Docker not running?**
```bash
# Start Docker Desktop, then:
docker compose -f realtime/infra/docker-compose.yml up -d
```

**Port conflicts?**
```bash
# Edit realtime/infra/docker-compose.yml
# Change port mappings, then restart
```

**Reset everything?**
```bash
docker compose -f realtime/infra/docker-compose.yml down -v
docker compose -f realtime/infra/docker-compose.yml up -d
```

---

**Ready to build the streaming pipeline! 🚀**
