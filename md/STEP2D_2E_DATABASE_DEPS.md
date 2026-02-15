# Step 2D & 2E Complete - Database Schema & Dependencies

## ✅ Step 2D: PostgreSQL Tables Created

### Table: `risk_scored`

**Purpose**: Store all scored loan events from the streaming pipeline

**Schema**:
```sql
CREATE TABLE risk_scored (
  id BIGSERIAL PRIMARY KEY,
  event_time TIMESTAMPTZ DEFAULT NOW(),
  loan_id TEXT,
  purpose TEXT,
  term TEXT,
  loan_amnt DOUBLE PRECISION,
  annual_inc DOUBLE PRECISION,
  dti DOUBLE PRECISION,
  int_rate_pct DOUBLE PRECISION,
  revol_util_pct DOUBLE PRECISION,
  delinq_2yrs DOUBLE PRECISION,
  inq_last_6mths DOUBLE PRECISION,
  credit_history_years DOUBLE PRECISION,
  emp_length_yrs DOUBLE PRECISION,
  dti_band TEXT,
  util_band TEXT,
  rate_band TEXT,
  early_warning_flag INTEGER,
  risk_tier TEXT,
  reasons TEXT
);
```

### Indexes Created

1. **`idx_risk_scored_time`** - Time-based queries (DESC order)
   ```sql
   CREATE INDEX idx_risk_scored_time ON risk_scored(event_time DESC);
   ```
   - Use case: Get recent scored loans
   - Query: `SELECT * FROM risk_scored ORDER BY event_time DESC LIMIT 100;`

2. **`idx_risk_scored_tier`** - Risk tier filtering
   ```sql
   CREATE INDEX idx_risk_scored_tier ON risk_scored(risk_tier);
   ```
   - Use case: Get all watchlist loans
   - Query: `SELECT * FROM risk_scored WHERE risk_tier = 'Watchlist';`

3. **`risk_scored_pkey`** - Primary key (auto-created)
   ```sql
   CREATE UNIQUE INDEX risk_scored_pkey ON risk_scored(id);
   ```

### Verification

**Table columns** (20 total):
```
     column_name      |        data_type         
----------------------+--------------------------
 id                   | bigint
 event_time           | timestamp with time zone
 loan_id              | text
 purpose              | text
 term                 | text
 loan_amnt            | double precision
 annual_inc           | double precision
 dti                  | double precision
 int_rate_pct         | double precision
 revol_util_pct       | double precision
 delinq_2yrs          | double precision
 inq_last_6mths       | double precision
 credit_history_years | double precision
 emp_length_yrs       | double precision
 dti_band             | text
 util_band            | text
 rate_band            | text
 early_warning_flag   | integer
 risk_tier            | text
 reasons              | text
```

**Indexes** (3 total):
```
      indexname       |                     indexdef                                        
----------------------+---------------------------------------------------------------------
 risk_scored_pkey     | CREATE UNIQUE INDEX ... ON risk_scored USING btree (id)
 idx_risk_scored_time | CREATE INDEX ... ON risk_scored USING btree (event_time DESC)
 idx_risk_scored_tier | CREATE INDEX ... ON risk_scored USING btree (risk_tier)
```

### Schema File

**Location**: `realtime/infra/schema.sql`

This file can be used to recreate the schema:
```bash
docker exec -i credit-risk-postgres psql -U credit -d credit_risk < realtime/infra/schema.sql
```

---

## ✅ Step 2E: Streaming Dependencies Added

### Dependencies Installed

Added to `requirements.txt`:

1. **`kafka-python`** (v2.3.0)
   - Purpose: Kafka producer and consumer
   - Use: Publish/subscribe to loan application events
   - Docs: https://kafka-python.readthedocs.io/

2. **`psycopg2-binary`** (v2.9.11)
   - Purpose: PostgreSQL database adapter
   - Use: Insert scored events into `risk_scored` table
   - Docs: https://www.psycopg.org/

3. **`python-dotenv`** (v1.2.1)
   - Purpose: Load environment variables from `.env` file
   - Use: Manage configuration (DB credentials, Kafka URLs)
   - Docs: https://github.com/theskumar/python-dotenv

### Installation

```bash
source .venv/bin/activate
pip install kafka-python psycopg2-binary python-dotenv
```

**Status**: ✅ All dependencies installed successfully

### Updated requirements.txt

```text
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.3.2
matplotlib==3.8.2

# Streaming dependencies (Step 2E)
kafka-python
psycopg2-binary
python-dotenv
```

---

## 🧪 Testing Database Connection

### Test PostgreSQL Connection

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="credit_risk",
    user="credit",
    password="risk"
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM risk_scored;")
count = cursor.fetchone()[0]
print(f"Rows in risk_scored: {count}")

cursor.close()
conn.close()
```

### Test Kafka Connection

```python
from kafka import KafkaProducer, KafkaConsumer

# Test producer
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('test-topic', b'Hello Kafka!')
producer.flush()
producer.close()

print("✅ Kafka producer working!")
```

### Test Environment Variables

Create `.env` file:
```bash
DATABASE_URL=postgresql://credit:risk@localhost:5433/credit_risk
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL")
kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

print(f"Database: {db_url}")
print(f"Kafka: {kafka_servers}")
```

---

## 📊 Example: Insert Scored Event

```python
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="credit_risk",
    user="credit",
    password="risk"
)

cursor = conn.cursor()

# Insert a scored event
cursor.execute("""
    INSERT INTO risk_scored (
        loan_id, purpose, term, loan_amnt, annual_inc, dti,
        int_rate_pct, revol_util_pct, delinq_2yrs, inq_last_6mths,
        credit_history_years, emp_length_yrs,
        dti_band, util_band, rate_band,
        early_warning_flag, risk_tier, reasons
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
""", (
    'LOAN-12345',
    'debt_consolidation',
    '36 months',
    12000.0,
    55000.0,
    33.2,
    21.5,
    85.0,
    1.0,
    2.0,
    6.67,
    3.0,
    'High',
    'Very High',
    'Very High',
    1,
    'Watchlist',
    'DTI>=30,REVOL_UTIL>=80,DELINQ_2YRS>0,INQ_LAST_6MTHS>=2'
))

conn.commit()
cursor.close()
conn.close()

print("✅ Event inserted successfully!")
```

---

## 🎯 What's Ready

### Database
✅ **Table created**: `risk_scored` with 20 columns  
✅ **Indexes created**: Time-based and tier-based  
✅ **Schema file**: `realtime/infra/schema.sql`  

### Dependencies
✅ **Kafka client**: `kafka-python` installed  
✅ **PostgreSQL client**: `psycopg2-binary` installed  
✅ **Config management**: `python-dotenv` installed  

### Infrastructure
✅ **PostgreSQL**: Running on port 5433  
✅ **Redpanda (Kafka)**: Running on port 9092  
✅ **Redpanda Console**: Running on http://localhost:8080  

---

## 🚀 Next Steps (Step 3)

With database and dependencies ready, you can now build:

1. **Kafka Producer** (`realtime/streaming/producer.py`)
   - Read loan applications (CSV or API)
   - Publish to `loan-applications` topic
   - Use `kafka-python` library

2. **Kafka Consumer** (`realtime/streaming/consumer.py`)
   - Subscribe to `loan-applications` topic
   - Process with `preprocess_event()` and `apply_rules()`
   - Insert into `risk_scored` table using `psycopg2`
   - Publish to `scored-loans` topic

3. **Environment Configuration** (`.env`)
   - Database credentials
   - Kafka bootstrap servers
   - Topic names

---

## 📚 Files Created/Modified

**New Files**:
- `realtime/infra/schema.sql` - Database schema

**Modified Files**:
- `requirements.txt` - Added streaming dependencies

**Database Objects**:
- Table: `risk_scored`
- Indexes: `idx_risk_scored_time`, `idx_risk_scored_tier`

---

**Steps 2D & 2E Complete! Ready for streaming implementation! 🎉**
