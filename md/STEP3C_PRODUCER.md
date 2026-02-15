# Step 3C Complete - Kafka Producer Running

## ✅ Producer Successfully Sending Events

### Kafka Topic Created

```bash
$ docker exec -it redpanda rpk topic create loan_applications --partitions 3 --replicas 1

TOPIC              STATUS
loan_applications  OK
```

**Configuration**:
- **Topic**: `loan_applications`
- **Partitions**: 3
- **Replicas**: 1
- **Status**: ✅ Active

### Producer Execution

**Command**:
```bash
python realtime/streaming/producer.py --csv data/processed/sample_100k.csv --rate 200 --max 1000
```

**Result**:
```
✅ Sent 1000 events to topic 'loan_applications' in 6.79s (~147.2 eps)
```

**Performance**:
- **Events Sent**: 1,000
- **Duration**: 6.79 seconds
- **Throughput**: ~147 events/second
- **Target Rate**: 200 events/second
- **Status**: ✅ Success

### Message Verification

**Sample Message** (first event from topic):
```json
{
  "topic": "loan_applications",
  "key": "53595000",
  "value": {
    "id": 53595000,
    "loan_amnt": 15000.0,
    "term": " 36 months",
    "int_rate": "11.53",
    "installment": 494.86,
    "purpose": "credit_card",
    "annual_inc": 34221.0,
    "dti": 28.31,
    "delinq_2yrs": 0.0,
    "earliest_cr_line": "Apr-1997",
    "inq_last_6mths": 1.0,
    "open_acc": 9.0,
    "total_acc": 25.0,
    "revol_util": "53.2",
    "loan_status": "Charged Off",
    "event_time": "2026-02-14T06:46:51.628471+00:00",
    ...
  },
  "partition": 0,
  "offset": 0
}
```

**Key Features**:
- ✅ All loan fields included
- ✅ `event_time` timestamp added
- ✅ NaN values converted to `null`
- ✅ Keyed by loan ID for partitioning
- ✅ JSON serialized

---

## 📊 Producer Code Overview

**File**: `realtime/streaming/producer.py`

### Key Features

1. **Configurable Rate Control**
   - `--rate`: Events per second (default: 10)
   - `--max`: Maximum events to send (0 = all)
   - `--sleep`: Additional delay per event

2. **Kafka Configuration**
   - `acks="all"`: Wait for all replicas
   - `linger_ms=10`: Batch messages for efficiency
   - `retries=5`: Retry failed sends

3. **Data Handling**
   - Reads from CSV (pandas)
   - Converts NaN to None for clean JSON
   - Adds `event_time` timestamp
   - Uses loan ID as message key

4. **Performance**
   - Periodic flush every 200 messages
   - Rate limiting for controlled throughput
   - Efficient batching

### Usage Examples

**Slow steady stream** (5 events/second):
```bash
python realtime/streaming/producer.py --rate 5
```

**Quick burst** (1000 events fast):
```bash
python realtime/streaming/producer.py --csv data/processed/sample_100k.csv --rate 200 --max 1000
```

**Send all data** (at 10 eps):
```bash
python realtime/streaming/producer.py
```

**Custom CSV source**:
```bash
python realtime/streaming/producer.py --csv path/to/loans.csv --rate 50
```

---

## 🔍 Kafka Topic Status

### Topic Information

```bash
$ docker exec -it redpanda rpk topic list

NAME               PARTITIONS  REPLICAS
loan_applications  3           1
test-connectivity  1           1
```

### Topic Details

```bash
$ docker exec -it redpanda rpk topic describe loan_applications

SUMMARY
=======
NAME        loan_applications
PARTITIONS  3
REPLICAS    1
```

**Retention**: 7 days (604800000 ms)  
**Max Message Size**: 1 MB  
**Compression**: Producer-controlled

---

## 🧪 Testing Commands

### View Messages

**Consume 1 message**:
```bash
docker exec -it redpanda rpk topic consume loan_applications --num 1 --format json
```

**Consume from beginning**:
```bash
docker exec -it redpanda rpk topic consume loan_applications --offset start --num 10
```

**Tail the topic** (continuous):
```bash
docker exec -it redpanda rpk topic consume loan_applications --offset end
```

### Topic Management

**List topics**:
```bash
docker exec -it redpanda rpk topic list
```

**Describe topic**:
```bash
docker exec -it redpanda rpk topic describe loan_applications
```

**Delete topic** (if needed):
```bash
docker exec -it redpanda rpk topic delete loan_applications
```

---

## 🌐 Redpanda Console

You can also view the messages in the web UI:

1. Open: http://localhost:8080
2. Navigate to **Topics** → **loan_applications**
3. View messages, partitions, and consumer groups

**Features**:
- Browse messages
- Search by key/value
- View partition distribution
- Monitor consumer lag

---

## 📈 Performance Notes

### Observed Throughput

- **Target**: 200 events/second
- **Actual**: ~147 events/second
- **Reason**: CSV reading + JSON serialization overhead

### Optimization Tips

1. **Increase batch size**: Adjust `linger_ms` and batch size
2. **Reduce flushes**: Flush less frequently than every 200 messages
3. **Use Avro**: Binary serialization is faster than JSON
4. **Parallel producers**: Run multiple producer instances

### Production Considerations

- **Monitoring**: Track producer metrics (latency, errors)
- **Error handling**: Implement retry logic and dead letter queue
- **Schema validation**: Validate events before sending
- **Backpressure**: Handle slow consumers gracefully

---

## 🎯 What's Next

With 1000 events in Kafka, you're ready for:

### Step 3D: Build Consumer

Create `realtime/streaming/consumer.py` to:
1. Subscribe to `loan_applications` topic
2. Process each event with `preprocess_event()` and `apply_rules()`
3. Insert scored events into PostgreSQL `risk_scored` table
4. Optionally publish to `scored-loans` topic

**Example Consumer Flow**:
```
Kafka → Consumer → Preprocess → Rules → PostgreSQL
                                      ↓
                                  scored-loans topic
```

---

## 📚 Files

**Created**:
- `realtime/streaming/producer.py` - Kafka producer

**Kafka Objects**:
- Topic: `loan_applications` (3 partitions, 1000 messages)

**Documentation**:
- `STEP3C_PRODUCER.md` - This document

---

**Step 3C Complete! 1000 events ready for processing! 🎉**
