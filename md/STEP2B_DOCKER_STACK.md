# Step 2B Complete - Docker Stack Running

## ✅ **Stack Successfully Started!**

All containers are up and running:

```
CONTAINER ID   IMAGE                          STATUS                   PORTS
7cc8f2cf681f   redpandadata/redpanda:latest   Up (healthy)             9092, 8082, 9644
3e1d176808f9   redpandadata/console:latest    Up                       8080
43966cbd07ed   postgres:16                    Up (health: starting)    5433
```

---

## 🎯 **Services Available**

### 1. **Redpanda (Kafka-compatible)**
- **Container**: `redpanda`
- **Status**: ✅ Healthy
- **Ports**:
  - `9092` - Kafka API (for producers/consumers)
  - `8082` - Pandaproxy (HTTP REST API)
  - `9644` - Admin API

**Usage**:
```bash
# Test Kafka connection
docker exec -it redpanda rpk cluster info
```

---

### 2. **Redpanda Console (Web UI)**
- **Container**: `redpanda-console`
- **Status**: ✅ Running
- **Port**: `8080`
- **URL**: http://localhost:8080

**Access**: Open your browser and navigate to http://localhost:8080 to view:
- Topics
- Messages
- Consumer groups
- Cluster health

---

### 3. **PostgreSQL Database**
- **Container**: `credit-risk-postgres`
- **Status**: ✅ Running (health check starting)
- **Port**: `5433` (mapped to avoid conflict with existing PostgreSQL)
- **Credentials**:
  - User: `credit`
  - Password: `risk`
  - Database: `credit_risk`

**Connection String**:
```
postgresql://credit:risk@localhost:5433/credit_risk
```

**Usage**:
```bash
# Connect to PostgreSQL
docker exec -it credit-risk-postgres psql -U credit -d credit_risk

# Or from host (if psql installed)
psql -h localhost -p 5433 -U credit -d credit_risk
```

---

## 🔧 **Port Configuration**

| Service | Host Port | Container Port | Purpose |
|---------|-----------|----------------|---------|
| Redpanda (Kafka) | 9092 | 9092 | Kafka API |
| Redpanda (Proxy) | 8082 | 8082 | HTTP REST API |
| Redpanda (Admin) | 9644 | 9644 | Admin API |
| Console UI | 8080 | 8080 | Web Interface |
| PostgreSQL | **5433** | 5432 | Database |

**Note**: PostgreSQL uses port **5433** on the host to avoid conflict with your existing PostgreSQL instance on port 5432.

---

## 🧪 **Quick Tests**

### Test Redpanda (Kafka)
```bash
# Check cluster info
docker exec -it redpanda rpk cluster info

# Create a test topic
docker exec -it redpanda rpk topic create test-topic

# List topics
docker exec -it redpanda rpk topic list
```

### Test PostgreSQL
```bash
# Check database connection
docker exec -it credit-risk-postgres pg_isready -U credit -d credit_risk

# Connect to database
docker exec -it credit-risk-postgres psql -U credit -d credit_risk
```

### Test Console UI
Open your browser: http://localhost:8080

---

## 📊 **Useful Commands**

### View logs
```bash
# All services
docker compose -f realtime/infra/docker-compose.yml logs -f

# Specific service
docker compose -f realtime/infra/docker-compose.yml logs -f redpanda
docker compose -f realtime/infra/docker-compose.yml logs -f postgres
docker compose -f realtime/infra/docker-compose.yml logs -f console
```

### Stop the stack
```bash
docker compose -f realtime/infra/docker-compose.yml down
```

### Stop and remove volumes (clean slate)
```bash
docker compose -f realtime/infra/docker-compose.yml down -v
```

### Restart a service
```bash
docker compose -f realtime/infra/docker-compose.yml restart redpanda
docker compose -f realtime/infra/docker-compose.yml restart postgres
```

---

## 🚀 **Next Steps**

With the infrastructure running, you can now:

1. **Create Kafka topics** for loan applications
2. **Set up database schema** in PostgreSQL
3. **Build producer/consumer** applications
4. **Deploy your API** for real-time scoring

The foundation is ready! 🎉

---

## 🐛 **Troubleshooting**

### Container not healthy?
```bash
# Check health status
docker ps

# View logs
docker compose -f realtime/infra/docker-compose.yml logs postgres
```

### Port conflicts?
If you need to change ports, edit `realtime/infra/docker-compose.yml` and restart:
```bash
docker compose -f realtime/infra/docker-compose.yml down
docker compose -f realtime/infra/docker-compose.yml up -d
```

### Reset everything?
```bash
# Stop and remove all containers and volumes
docker compose -f realtime/infra/docker-compose.yml down -v

# Start fresh
docker compose -f realtime/infra/docker-compose.yml up -d
```
