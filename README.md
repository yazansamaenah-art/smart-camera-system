SmartPole — Citywide Intelligent Camera Platform (Beta)

Status: ✅ CI passing on camera

Unified edge-to-cloud platform for traffic monitoring, incident analytics, and smart-city camera infrastructure.
This repository is a production-ready skeleton for pilots and the foundation for a citywide rollout (with a dedicated ops/dev team).

What’s inside

Edge agent with pluggable AI backends (OpenCV / Tesseract / stub)

Cloud API (FastAPI): ingest, upload, policy/redaction, analytics, dashboard, Prometheus metrics

Workers (Kafka/MQTT) for high-scale ingestion

Fleet Manager microservice (register/heartbeat/config)

Deployments: Docker Compose (pilot) and Helm/Kubernetes (prod)

CI: GitHub Actions runs tests on every push/PR

Quick start (local)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit if needed
uvicorn cloud.app:app --host 0.0.0.0 --port 8000
# Health   : http://127.0.0.1:8000/health
# Dashboard: http://127.0.0.1:8000/
# Metrics  : http://127.0.0.1:8000/metrics


Run the edge agent in a second terminal:

source .venv/bin/activate
python smartpole/edge/agent.py --server http://127.0.0.1:8000 --backend opencv --iterations 20 --fps 4

Docker & Kubernetes

Compose (pilot): ops/compose/

Helm (prod): ops/helm/smartpole/ (includes HPA/PDB starter templates)

Docs

🧭 Architecture: ARCHITECTURE.md

🚀 Deployment guide: DEPLOYMENT.md

🧪 Tests: tests/

Citywide readiness (Beta)

This is a robust skeleton. For a full rollout, plan for managed Postgres, S3/GCS, Kafka/MQTT, Kubernetes autoscaling (HPA), secret management, centralized logging/alerting, and an SRE/DevOps team. Policies support PII redaction.

Contributing / License

Open beta; issues and PRs welcome (performance, models, dashboards, integrations).
Add a license file of your choice (e.g., MIT/Apache-2.0) before public deployments.
