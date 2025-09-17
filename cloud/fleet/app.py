import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="SmartPole Fleet Manager", version="0.1.0")

DEVICES: Dict[str, dict] = {}
CONFIGS: Dict[str, dict] = {"default": {"fps": 4, "backend": "opencv"}}
HEARTBEATS: Dict[str, float] = {}

class RegisterIn(BaseModel):
    device_id: str
    metadata: dict = {}

class ConfigIn(BaseModel):
    device_id: str
    config: dict

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/register")
def register(body: RegisterIn):
    DEVICES[body.device_id] = {"metadata": body.metadata, "registered": time.time()}
    HEARTBEATS[body.device_id] = time.time()
    return {"status": "ok"}

@app.post("/heartbeat/{device_id}")
def heartbeat(device_id: str):
    if device_id not in DEVICES:
        raise HTTPException(404, "Unknown device")
    HEARTBEATS[device_id] = time.time()
    return {"status": "ok"}

@app.get("/config/{device_id}")
def get_config(device_id: str):
    cfg = CONFIGS.get(device_id) or CONFIGS["default"]
    return {"device_id": device_id, "config": cfg}

@app.post("/config")
def set_config(body: ConfigIn):
    CONFIGS[body.device_id] = body.config
    return {"status": "ok"}

@app.get("/devices")
def devices():
    return {"devices": DEVICES, "heartbeats": HEARTBEATS}
