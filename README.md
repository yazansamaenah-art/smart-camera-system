
# SmartPole — Full Citywide Build (MVP + Auth + Storage + Dashboard + Workers + Fleet + Helm + CI)

This is a complete drop-in repo with:
- Edge agent + pluggable AI (stub/opencv/tesseract)
- Cloud API (FastAPI) with policy, DB, auth, image upload, analytics, metrics
- Object storage: local/S3/GCS
- Worker consumers: Kafka & MQTT (optional)
- Fleet Manager microservice
- Docker/Compose + Helm (with HPA/PDB templates)
- GitHub Actions CI
