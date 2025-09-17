# SmartPole — Citywide Intelligent Camera Platform (Beta)

> Unified **edge-to-cloud** platform for traffic monitoring, incident analytics, and smart-city camera infrastructure.  
> This repository is a **production-ready skeleton** for pilots and a foundation for citywide rollout (operated by the buyer or their integrator).

[![CI](https://github.com/yazansamaenah-art/smart-camera-system/actions/workflows/ci.yml/badge.svg?branch=camera)](https://github.com/yazansamaenah-art/smart-camera-system/actions/workflows/ci.yml)

---

## What’s inside
- **Edge agent** with pluggable AI backends (OpenCV / Tesseract / stub)
- **Cloud API (FastAPI)**: ingest, upload, policy/redaction, analytics, dashboard, Prometheus metrics
- **Workers** (Kafka/MQTT) for scale-out ingestion (optional)
- **Fleet Manager** microservice (register/heartbeat/config)
- **Deployments**: Docker Compose (pilot) and Helm/Kubernetes (production)
- **CI**: GitHub Actions runs tests on every push/PR

---

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit if needed
uvicorn cloud.app:app --host 0.0.0.0 --port 8000
# Health   : http://127.0.0.1:8000/health
# Dashboard: http://127.0.0.1:8000/
# Metrics  : http://127.0.0.1:8000/metrics
Run the edge agent (second terminal):

bash
Copy code
source .venv/bin/activate
python smartpole/edge/agent.py --server http://127.0.0.1:8000 --backend opencv --iterations 20 --fps 4
Docker & Kubernetes
Compose (pilot): ops/compose/

Helm (prod): ops/helm/smartpole/ (HPA/PDB templates included)

Configuration
Copy .env.example to .env. Common variables:

Variable	Example	Notes
DATABASE_URL	sqlite:///./smartpole.db	Use Postgres in prod
BLOBS_DIR	blobs	Local image storage if not using S3/GCS
S3_BUCKET / GCS_BUCKET	my-bucket	Use one; provide cloud creds
API_KEY / JWT_SECRET	dev-key-123	Edge/worker auth headers
PIPELINE_BACKEND	opencv	opencv / tesseract / stub
KAFKA_BROKERS / MQTT_BROKER	broker:9092	Optional scale-out

Documentation
🧭 Architecture: ARCHITECTURE.md

🚀 Deployment guide: DEPLOYMENT.md

📄 Master SOW (no maintenance): contracts/MASTER_SOW.md

🧾 Order Form (template): contracts/ORDER_FORM_TEMPLATE.md

⚖️ EULA: EULA.md · License: LICENSE

Citywide readiness (Beta)
This is a robust skeleton. For a full rollout, buyers should plan for: managed Postgres, S3/GCS, Kafka/MQTT, Kubernetes with autoscaling (HPA), secret management, centralized logging/alerting, and an SRE/DevOps function. Policies support PII redaction.

Releases
Current tag: v1.0-initial.

Use the release’s Source code (zip) for the exact, frozen package matching the tag.

Commercial terms
Use governed by the EULA; delivery/acceptance by the Master SOW.
Per-city/per-agency perpetual license; no resale/sublicensing/hosting for third parties.

Support policy: This is delivered one-time, “AS IS”. No maintenance, updates, or training are provided by the provider. Operation is the responsibility of the buyer or their integrator.

FAQ (Common questions)
Q: Can you transfer the repo or run it for us?
A: This is a one-time delivery. Please import the release ZIP into your own systems/repo and operate it internally or via an integrator.

Q: Do you provide updates or support?
A: No. The license is download-only with no maintenance. See EULA and Master SOW.

Q: What do we need to configure?
A: Follow DEPLOYMENT.md: set up DB (Postgres recommended), object storage (S3/GCS), and create .env from .env.example.

Q: Can we use this for multiple cities/agencies?
A: Each city/agency requires its own Order (license). See EULA/SOW.

Q: Where do we see system health?
A: /health and /metrics on the Cloud API; dashboard at /.

