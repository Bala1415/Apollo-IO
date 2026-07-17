# Disaster Recovery & Backup Strategy

## 1. Database Backup Strategy

PostgreSQL is the single source of truth for the Apollo-IO platform. 

### Automated Backups
If using a managed service (AWS RDS), configure:
- **Automated Snapshots**: Daily automated snapshots with a 30-day retention period.
- **Point-in-Time Recovery (PITR)**: Enable transaction log archiving (WAL) to restore to any specific second within the last 7 days.

### Manual / Self-Hosted Backups
If using the `docker-compose.yml` DB container, schedule a cron job utilizing `pg_dump`:
```bash
docker exec -t apollo_db pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```
Store these backups in a secure offsite location (e.g., AWS S3 Glacier).

## 2. Restore Procedures

In the event of a catastrophic database failure:

1. Stop the `api` and `worker` containers to prevent malformed data ingestion.
2. Spin up a fresh `db` container.
3. Import the SQL dump:
```bash
cat your_dump.sql | docker exec -i apollo_db psql -U postgres
```
4. Restart the API and Worker services.

## 3. High Availability

To minimize the need for disaster recovery:
- Run PostgreSQL in a Multi-AZ cluster.
- Utilize Redis Clusters for session/queue replication.
- Configure Kubernetes Horizontal Pod Autoscalers (HPA) to handle sudden spikes in API traffic, preventing Out Of Memory (OOM) crashes.
