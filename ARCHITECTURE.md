SmartPole — System Architecture (Beta)

SmartPole is an edge-to-cloud platform for intelligent traffic monitoring and incident analytics.
This document explains how it works, the data flow, and how it scales citywide.

High-Level Diagram
flowchart LR
    subgraph Edge["Edge (Intersection / Camera Pole)"]
      CAM[Camera\n+ Sensors] --> AGENT[Edge Agent\n(AI Pipeline: OpenCV/Tesseract)]
      AGENT -->|HTTPS + Auth| UPLOAD[/POST /upload (image)/]
      AGENT -->|HTTPS + Auth|\nINGEST[/POST /ingest (event)/]
    end

    subgraph Cloud["Cloud (FastAPI)"]
      UPLOAD --> BLOB[(Object Storage\nLocal / S3 / GCS)]
      INGEST --> POLICY[Policy Engine\n(allow/deny/redact)]
      POLICY --> DB[(Database\nSQLite / Postgres)]
      DB --> API[API Endpoints\n/events, /analytics, /metrics, /health]
      API --> DASH[Dashboard\n(HTML UI)]
    end

    subgraph CityScale["City Scale (Optional)"]
      KAFKA[(Kafka)]:::q --> WORKER[Worker\nconsumer_kafka.py]:::svc
      MQTT[(MQTT)]:::q --> WM[Worker\nconsumer_mqtt.py]:::svc
      WORKER -->|/ingest/message| INGEST
      WM -->|/ingest/message| INGEST
      FLEET[Fleet Manager\nRegister/Heartbeat/Config]:::svc --> AGENT
    end

    classDef q fill:#fff,stroke:#333,stroke-width:1px;
    classDef svc fill:#E7F2FF,stroke:#1B76D1,stroke-width:1px;

Components
Edge Agent (smartpole/edge)

Sensors/HAL: hal/sensors.py simulates camera frames, GPS, and air quality.

AI Pipeline: ai/pipeline.py pluggable backends:

opencv (default), tesseract, or stub.

Agent: agent.py captures frames, runs inference, uploads the JPEG, and posts an event (/ingest).

Auth headers: x-api-key: <API_KEY> and/or Authorization: Bearer <JWT>.

Cloud API (cloud)

FastAPI app: cloud/app.py

POST /upload → returns image URL (local /blobs/*, S3, or GCS)

POST /ingest → validates + policy-filtered event → DB

GET /events → recent events (for dashboard)

GET /analytics/counts, GET /analytics/last24h

GET /metrics → Prometheus metrics

GET / → simple HTML dashboard

DB models: cloud/models.py (SQLAlchemy)

Policy Engine: cloud/policy/engine.py + policy/rules.yaml

allow_event_types, deny_event_types, redact_fields (e.g., plate text)

Workers (worker/)

Kafka consumer: consumer_kafka.py reads topic → POST /ingest/message

MQTT consumer: consumer_mqtt.py subscribes → POST /ingest/message

Used when scale requires message buses between edge and cloud.

Fleet Manager (cloud/fleet/app.py)

Register devices: /register

Health: /heartbeat/{device_id}

Remote config: /config/{device_id} (get/set)

Foundation for provisioning, rotation, and policy rollout.

Data Flow

Capture & Inference (Edge)
Camera frame → AI pipeline detects objects/plates → event payload.

Upload
Agent posts JPEG to POST /upload → returns image URL (local/S3/GCS).

Ingest
Agent posts event to POST /ingest including the image URL.

Policy
Cloud applies allow/deny and redaction rules (e.g., strip plate text).

Persist & Serve
Event saved to DB; dashboard and analytics render recent data.

Scale (optional)
Edge → Kafka/MQTT → workers → /ingest/message → same policy/DB path.

Authentication & Security

Headers: x-api-key (static) and/or Authorization: Bearer <JWT>.

Secrets: set API_KEY / JWT_SECRET (use a secret manager in prod).

Transport: terminate TLS at ingress/gateway; mTLS recommended for device → cloud in production.

Policy: treat PII (e.g., plate text) with redact_fields in rules.yaml.

Storage

Database:

Pilot: SQLite (sqlite:///./smartpole.db)

Production: PostgreSQL (postgresql+psycopg2://user:pass@host:5432/db)

Object Storage:

Local dev: /blobs (served at /blobs/...)

Production: S3 (S3_BUCKET) or GCS (GCS_BUCKET) with lifecycle rules.

Scaling & Deployment

Docker:

Cloud + Edge (Compose) → ops/compose/docker-compose.yml

Optional workers + Fleet → overlay compose

Kubernetes:

Helm chart in ops/helm/smartpole (Service + Deployment)

Additions for HPA/PDB in values-additions.yaml and templates-additions.yaml

Message Buses: Kafka/MQTT increase throughput and decouple edge from API.

Observability & Operations

Health: /health

Metrics: /metrics (Prometheus counters + histograms)

Analytics: /analytics/counts, /analytics/last24h

Dashboard: / (auto-refresh)

CI: GitHub Actions runs tests on each push/PR (.github/workflows/ci.yml)

Citywide Readiness (Beta)

This repository is a production-ready skeleton:

Works end-to-end (Edge → Cloud → Dashboard/Analytics).

Suitable for pilots and as a foundation for city deployments.

For a full metropolitan rollout, plan for:

Managed Postgres, S3/GCS, Kafka/MQTT with monitoring & retention

Kubernetes with HPA, blue/green or canary, and rollback

Secret management (KMS/Secrets Manager), key rotation, network policies

Centralized logging (ELK/Cloud Logging) + Alerting (Prometheus/Alertmanager)

SRE/DevOps on-call for SLAs, security hardening, and incident response

Model/AI lifecycle: calibration, labeling, accuracy monitoring, periodic retraining

Key Endpoints

POST /upload → returns image URL

POST /ingest / POST /ingest/message → event intake

GET /events → recent events (dashboard)

GET /analytics/counts, GET /analytics/last24h

GET /metrics, GET /health

References

Deployment steps: DEPLOYMENT.md

Example policies: cloud/policy/rules.yaml

Tests: tests/ (policy, sensors, pipeline)

Status: Beta — strong skeleton with working components, intended to be extended and hardened by a dedicated team for citywide production use.
