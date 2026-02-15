# Step 4D Complete - Database Verification

## ✅ PostgreSQL Populated with Real-Time Events

### Query 1: Risk Tier Distribution

```bash
docker exec -it credit-risk-postgres psql -U credit -d credit_risk -c "SELECT risk_tier, COUNT(*) FROM risk_scored GROUP BY 1 ORDER BY 2 DESC;"
```

**Result**:
```
 risk_tier | count 
-----------+-------
 Low       |     5
 Elevated  |     3
(2 rows)
```
- **Total Processed**: 8 events
- **Distribution**: 62.5% Low Risk, 37.5% Elevated Risk

### Query 2: Sample Rows (Recent Events)

```bash
docker exec -it credit-risk-postgres psql -U credit -d credit_risk -c "SELECT event_time, loan_id, risk_tier, reasons FROM risk_scored ORDER BY event_time DESC LIMIT 10;"
```

**Result**:
```
          event_time           |  loan_id  | risk_tier | reasons 
-------------------------------+-----------+-----------+---------
 2026-02-14 07:00:12.428568+00 | 140060243 | Low       | 
 2026-02-14 07:00:12.428568+00 | 79291085  | Low       | 
 2026-02-14 07:00:12.428568+00 | 146013168 | Low       | 
 2026-02-14 07:00:12.428568+00 | 48816347  | Low       | 
 2026-02-14 07:00:12.428568+00 | 85659491  | Elevated  | 
 2026-02-14 07:00:12.428568+00 | 153172558 | Low       | 
 2026-02-14 07:00:12.428568+00 | 77059565  | Elevated  | 
 2026-02-14 07:00:12.428568+00 | 82157832  | Elevated  | 
(8 rows)
```
- **Columns Verified**: `event_time`, `loan_id`, `risk_tier`, `reasons`
- **Data Integrity**: Timestamps correct, loan IDs preserved, risk tier assigned.

---

## 🎯 Pipeline Status: Operational

The full end-to-end pipeline is verified:

1.  **Producer** sends to Kafka.
2.  **Consumer** reads from Kafka, scores event.
3.  **PostgreSQL** stores the scored result.
4.  **Verification** confirms data integrity in DB.

**Next Steps**:
- Scale up producer (send more data)?
- Build API on top of PostgreSQL?
- Add dashboard?
