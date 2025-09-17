
# SmartPole — Unified Intelligent Camera Platform (MVP + Deploy + Extras)

Working platform with:
- **Edge Agent** (synthetic camera + GPS + AQI → AI → events + image upload)
- **Cloud API (FastAPI)** with **Auth** (API key/JWT), **Policy Engine**, **DB**, **Object Storage**
- **Dashboard** at `/` (filters + live refresh, shows images)
- **Docker Compose** and **Helm** (starter) for deploy
- **Tests**

See `.env.example` for config.

## Local run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn cloud.app:app --reload --port 8000
# new terminal
python smartpole/edge/agent.py --server http://127.0.0.1:8000 --backend opencv --iterations 20
```
Open `http://127.0.0.1:8000/`.

## Docker
```bash
docker compose -f ops/compose/docker-compose.yml up --build
```

## Optional Production Features
- **Auth**: API key or JWT (env: `API_KEY` or `JWT_SECRET`).
- **Object storage**: Local disk (default), **S3** (`S3_BUCKET`, `AWS_*`) or **GCS** (`GCS_BUCKET`).
- **Postgres**: use `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db`.
- **Pluggable AI**: `PIPELINE_BACKEND=stub|opencv|tesseract`.
