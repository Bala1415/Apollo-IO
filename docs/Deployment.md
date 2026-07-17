# Apollo-IO Production Deployment Guide

## Infrastructure Architecture

Apollo-IO is designed for cloud-native deployments utilizing Docker and Kubernetes (or Docker Compose for single-node instances).

The complete production stack consists of:
1. **Nginx**: Edge reverse proxy, SSL termination, and rate limiting.
2. **FastAPI**: Synchronous REST API edge handling HTTP traffic.
3. **Background Worker**: Asynchronous execution engine running LangGraph agents.
4. **PostgreSQL 15**: Relational persistence and GraphState storage.
5. **Redis 7**: Distributed caching and background job queuing.
6. **Prometheus**: Metrics scraping and observability.

## Single-Node Deployment (Docker Compose)

The fastest path to production on an AWS EC2 or DigitalOcean droplet is via Docker Compose.

### 1. Environment Preparation
Ensure your `.env` file is populated with production secrets:
```env
DATABASE_URL=postgresql://postgres:secure_password@db:5432/apollo
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=production
SECRET_KEY=your_generated_secure_key
```

### 2. Launching the Stack
Run the orchestration command:
```bash
docker-compose up -d --build
```
This will automatically:
- Build the optimized, multi-stage Python image.
- Provision Postgres and Redis with persistent volumes.
- Mount the Nginx configuration.
- Expose the API on ports `80` and `443` (requires SSL certs).

### 3. Verification
Verify the health of the entire stack by hitting the deep health check:
```bash
curl http://localhost/health
```
Expect a `200 OK` with status `ok` for `database`, `providers`, and `system`.

## Kubernetes Deployment (AWS EKS / GCP GKE)

For distributed enterprise scaling, deploy the compiled container (`ghcr.io/your-repo/apollo-io-backend:latest`) across multiple pods.

- **API Pods**: Scale horizontally based on CPU utilization.
- **Worker Pods**: Scale based on the Redis Queue length (KEDA recommended).
- **Database**: Use a managed service like AWS RDS PostgreSQL instead of containerized DBs.
- **Redis**: Use AWS ElastiCache.
