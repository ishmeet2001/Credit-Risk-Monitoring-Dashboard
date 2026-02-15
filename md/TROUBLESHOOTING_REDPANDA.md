# Issue: Redpanda Console Connection Error

## Problem
The Redpanda Console was failing to connect to the Redpanda broker with `dial tcp [::1]:9092: connect: connection refused`.
This happened because Redpanda was advertising `localhost:9092` to the console, which the console interpreted as its own container's localhost (IPv6), preventing it from reaching the broker.

## Solution
1. **Updated Redpanda Configuration in `docker-compose.yml`**:
   - Added a second listener on port `29092` for internal Docker network communication.
   - Configured Redpanda to advertise `redpanda:29092` to internal clients (like the console) and `localhost:9092` to external clients (like the host machine).

2. **Updated Redpanda Console Configuration**:
   - Changed `KAFKA_BROKERS` to `redpanda:29092` to use the internal Docker network address.

## Verification
- Restarted the stack: `docker compose -f realtime/infra/docker-compose.yml up -d --force-recreate`
- Verified console logs: `docker logs redpanda-console` showed successful connection.
- Resent test data: Producer successfully sent 1000 events to `loan_applications`.

## Current Status
✅ Redpanda Console is now accessible at http://localhost:8080 and showing topics/messages.
✅ Producer can send messages from the host machine using `localhost:9092`.
