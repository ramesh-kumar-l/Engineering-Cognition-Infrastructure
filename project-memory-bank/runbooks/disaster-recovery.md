# Disaster Recovery Runbook

> **Owner:** Project lead
> **Last reviewed:** 2026-05-31
> **RTO target:** 2 hours | **RPO target:** 24 hours

## Scope

This runbook covers recovery for:
1. Postgres data loss / corruption.
2. Blob store (S3 / local filesystem) data loss.
3. Full environment destruction (host or cluster failure).

---

## 1. Backup Procedures

### 1.1 Postgres

**Cadence:** Daily at 02:00 UTC via cron or managed-DB automated backups.

```bash
# pg_dump to S3 (run from a job/cron with AWS credentials)
DATE=$(date +%Y%m%d)
pg_dump "$ECI_DB_URL" --format=custom --file="/tmp/eci-db-$DATE.dump"
aws s3 cp "/tmp/eci-db-$DATE.dump" "s3://${BACKUP_BUCKET}/postgres/eci-db-$DATE.dump"
rm "/tmp/eci-db-$DATE.dump"
```

**Retention:** 30 daily snapshots kept; weekly snapshot retained 1 year.

**Verify backup integrity (weekly):**
```bash
pg_restore --list "s3://${BACKUP_BUCKET}/postgres/eci-db-${DATE}.dump" | head -20
```

### 1.2 Blob store (S3 backend)

Enable S3 cross-region replication on `${ECI_BLOB_S3_BUCKET}` to a secondary bucket
in a different AWS region. Replication is async; RPO ≤ 15 min for object writes.

**Verify replication (weekly):**
```bash
aws s3 ls "s3://${BACKUP_BUCKET_SECONDARY}/blobs/" | wc -l
# Compare count to primary bucket
```

### 1.3 Local blob store (dev only)

Not supported for production. Use S3 backend with replication for production
(`ECI_BLOB_BACKEND=s3`).

---

## 2. Restore Procedures

### 2.1 Restore Postgres

```bash
# 1. Identify the backup to restore
aws s3 ls "s3://${BACKUP_BUCKET}/postgres/" | sort | tail -5

# 2. Download the chosen dump
aws s3 cp "s3://${BACKUP_BUCKET}/postgres/eci-db-${DATE}.dump" /tmp/restore.dump

# 3. Drop and recreate the database (DESTRUCTIVE — confirm with team first)
psql "$ECI_DB_URL_ADMIN" -c "DROP DATABASE eci;"
psql "$ECI_DB_URL_ADMIN" -c "CREATE DATABASE eci OWNER eci;"

# 4. Restore
pg_restore --dbname="$ECI_DB_URL" --no-owner /tmp/restore.dump

# 5. Verify row counts on key tables
psql "$ECI_DB_URL" -c "SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;"
```

### 2.2 Restore blob store

If using S3 with cross-region replication, promote the secondary bucket:
```bash
# Update ECI_BLOB_S3_BUCKET env var to point to the secondary bucket
# Redeploy API pods
```

If using the primary bucket (partial loss), use S3 versioning to restore:
```bash
aws s3api list-object-versions --bucket "${ECI_BLOB_S3_BUCKET}" \
  --prefix "blobs/" --query "DeleteMarkers[*].Key" --output text \
  | xargs -I {} aws s3api delete-object --bucket "${ECI_BLOB_S3_BUCKET}" --key {}
```

### 2.3 Verify data integrity after restore

```bash
# Run the integration test suite against the restored DB
ECI_TEST_DB_URL="$ECI_DB_URL" uv run pytest -m integration -q

# Run the eval gate
uv run python scripts/eval_gate.py
```

---

## 3. DR Drill Protocol

A DR drill must be executed before GA and quarterly thereafter.

### Drill steps

1. **Announce drill** to all stakeholders (Slack / email) with a 30-min window.
2. **Snapshot** the current DB to a dedicated drill backup prefix.
3. **Simulate failure**: rename the production DB, point `ECI_DB_URL` to a blank DB.
4. **Execute restore** following Section 2.1 against the drill backup.
5. **Run integrity checks** (integration tests + eval gate).
6. **Measure elapsed time** from step 3 to passing integrity checks.
7. **Record results** in the Drill Log below.
8. **Restore production** environment to the original state.

### Drill Log

| Date | Scenario | RTO achieved | RPO (data age) | Passed? | Notes |
|------|----------|-------------|----------------|---------|-------|
| TBD  | Full DB loss | — | — | — | First drill; schedule within 2 weeks of GA |

---

## 4. Contacts and Escalation

| Role | Responsibility |
|------|---------------|
| Project lead | DR owner; approves restore decisions |
| On-call engineer | Executes runbook; escalates to project lead if RTO at risk |

---

## 5. Known Gaps (as of P8 GA)

- Ollama model weights are not backed up — restore requires re-pull from Ollama registry.
- Langfuse traces are not in the DB backup — LLM observability history is lost on full restore.
- These gaps are accepted; recorded in `risk-register/risks.md` as R-S5.
