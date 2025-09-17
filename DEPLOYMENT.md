SmartPole – Citywide Intelligent Camera Platform (Beta)
This guide shows how to run SmartPole locally, with Docker, and in production (Kubernetes). It also covers environment variables, security, observability, and common troubleshooting.

1) Repository layout
cloud/                  # FastAPI cloud API (ingest, upload, analytics, metrics)
smartpole/edge/         # Edge agent, AI pipeline, sensors
worker/                 # Kafka + MQTT consumers (optional)
ops/docker/             # Dockerfiles
ops/compose/            # Docker Compose files
ops/helm/smartpole/     # Minimal Helm chart (+ HPA/PDB add-ons)
.github/workflows/      # CI pipeline (pytest)
.env.example            # Example env configuration
tests/                  # Unit tests

2) Environment variables

Copy .env.example → .env and adjust as needed.

Variable	Purpose	Example
DATABASE_URL	SQLAlchemy URL (SQLite for pilots; Postgres in prod)	sqlite:///./smartpole.db / postgresql+psycopg2://user:pass@host:5432/db
POLICY_FILE	Policy rules (allow/deny/redact)	cloud/policy/rules.yaml
API_KEY	Simple header auth for edge/worker	dev-key-123
JWT_SECRET	Optional JWT verification	dev-secret-123
BLOBS_DIR	Local image store (when not using S3/GCS)	blobs
S3_BUCKET + AWS creds	Enable S3 image storage	my-bucket
GCS_BUCKET	Enable GCS image storage	my-gcs-bucket
PIPELINE_BACKEND	Edge AI backend (opencv, tesseract, stub)	opencv
KAFKA_BROKERS / KAFKA_TOPIC	Kafka ingestion (optional)	broker:9092 / smartpole.events
MQTT_BROKER / MQTT_TOPIC	MQTT ingestion (optional)	broker.host / smartpole/events

For production, prefer Postgres, S3/GCS, and a real secret manager for keys.

3) Run locally (no containers)
3.1 Cloud API
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit as needed
uvicorn cloud.app:app --host 0.0.0.0 --port 8000


Check:

Health: http://127.0.0.1:8000/health

Dashboard: http://127.0.0.1:8000/

Metrics: http://127.0.0.1:8000/metrics

3.2 Edge agent (sends events to the cloud)

In a second terminal:

source .venv/bin/activate
python smartpole/edge/agent.py \
  --server http://127.0.0.1:8000 \
  --backend opencv \
  --iterations 20 \
  --fps 4

3.3 Quick curl tests
curl http://127.0.0.1:8000/events
curl http://127.0.0.1:8000/analytics/counts

4) Docker Compose (pilot)
4.1 Base (cloud + edge)
docker compose -f ops/compose/docker-compose.yml up --build
# cloud: http://localhost:8000

4.2 Add workers + fleet (overlay)
docker compose \
  -f ops/compose/docker-compose.yml \
  -f ops/compose/docker-compose.overlay.yml up --build
# fleet: http://localhost:8080


To use API key/JWT: set API_KEY/JWT_SECRET in .env and pass headers from the edge agent.

5) Kubernetes (production)

The included chart is a starter. You will likely add Ingress, secrets, and a managed database.

5.1 Build & push image
# Example using docker hub
docker build -f ops/docker/cloud.Dockerfile -t <your-registry>/smartpole-cloud:latest .
docker push <your-registry>/smartpole-cloud:latest

5.2 Install chart

Edit ops/helm/smartpole/values.yaml:

image:
  repository: <your-registry>/smartpole-cloud
  tag: latest
service:
  type: ClusterIP
  port: 8000


Install:

helm install smartpole ops/helm/smartpole

5.3 Enable autoscaling & PDBs (optional)

Use values-additions.yaml + templates-additions.yaml (HPA/PDB starter examples).
Integrate with your Prometheus Operator if you want ServiceMonitor.

6) Postgres, S3/GCS, Kafka/MQTT
6.1 Postgres

Set DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db

Ensure network access and SSL as required.

Run migrations by starting the app (SQLAlchemy will create tables on first run).

6.2 S3 / GCS for image storage

Set S3_BUCKET + AWS credentials or GCS_BUCKET + service account.

App will write uploaded JPEGs to the configured bucket; otherwise falls back to local BLOBS_DIR.

6.3 Kafka / MQTT

Kafka: set KAFKA_BROKERS and run worker/consumer_kafka.py (container provided in overlay compose).

MQTT: set MQTT_BROKER and run worker/consumer_mqtt.py.

7) Security

Auth: Use API_KEY or JWT_SECRET (or both).

Edge/worker: send header x-api-key: <key> or Authorization: Bearer <jwt>.

TLS: Terminate TLS at your ingress/API gateway or use mTLS between devices and the fleet/cloud.

Policies: Adjust cloud/policy/rules.yaml for allow/deny/redact (PII like plate text is redacted by default in the example).

8) Observability & Ops

Metrics: Prometheus at /metrics (ingest counter, latency histograms).

Health: /health

Analytics:

GET /analytics/counts (totals, by event type)

GET /analytics/last24h (rolling)

Dashboard: GET / (simple HTML table that auto-refreshes)

9) CI / CD

GitHub Actions workflow runs on every push/PR:

Installs system libs (libgl1, libglib2.0-0, tesseract-ocr)

Installs Python deps

Runs unit tests under tests/

Green ✅ = safe to deploy. Red ❌ = check logs in Actions tab.

10) Citywide rollout guidance (Beta)

This repo is a production-ready skeleton suitable for pilots and as a foundation for city deployments.
A citywide rollout should include:

Managed Postgres (HA), S3/GCS with lifecycle policies, and backups

Kafka or MQTT with monitoring & retention tuned for volume

Kubernetes with autoscaling (HPA), rolling deploys, and canary/rollback

Secret management (KMS/Parameter Store/Secrets Manager)

Centralized logging (ELK/Cloud Logging) and alerting (Prometheus/Alertmanager)

SRE/DevOps on-call for uptime SLAs and incident response

Security hardening (mTLS for devices, API keys rotation, network policies)

11) Troubleshooting

PyTest errors during collection

Ensure these package markers exist (empty files):

cloud/__init__.py
smartpole/__init__.py
smartpole/edge/__init__.py
smartpole/edge/ai/__init__.py
smartpole/edge/hal/__init__.py


ImportError: libGL.so.1 / OpenCV fails on CI

Make sure CI installs system packages:

sudo apt-get update
sudo apt-get install -y libgl1 libglib2.0-0 tesseract-ocr


Images not showing in dashboard

If not using S3/GCS, verify BLOBS_DIR exists and /blobs is mounted/writable.

401 Unauthorized

Set API_KEY (and/or JWT_SECRET) and send headers from edge/worker.

12) Useful endpoints

POST /upload – multipart image upload → returns URL (local/S3/GCS)

POST /ingest – JSON event body

POST /ingest/message – wrapper for worker payloads (Kafka/MQTT)

GET /events – recent events

GET /analytics/counts – totals/by-type

GET /metrics – Prometheus

Fleet (microservice): /register, /heartbeat/{device_id}, /config/{device_id}, /devices

13) Contact / Contributions

This is an open beta intended as a robust starting point.
Issues and PRs welcome: performance, models, dashboards, integrations.

End of DEPLOYMENT.md

Add deployment guide with local, docker, and Kubernetes setup instructions
