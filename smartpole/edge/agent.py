import argparse, time, os, yaml, requests, cv2
from .hal.sensors import SensorHub
from .ai.pipeline import AIPipeline

def build_event(ts, gps, ai_out, image_url=None):
    etype = "traffic_violation" if ai_out.get("plates") else ("presence" if ai_out.get("objects") else "presence")
    payload = {"objects": ai_out.get("objects",[]), "plates": ai_out.get("plates",[])}
    if image_url: payload["image_url"]=image_url
    return {"timestamp": ts, "type": etype, "location": {"lat": gps[0], "lon": gps[1]}, "payload": payload, "source":"edge"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--server", default=os.environ.get("SERVER_URL","http://127.0.0.1:8000"))
    p.add_argument("--iterations", type=int, default=int(os.environ.get("ITERATIONS","50")))
    p.add_argument("--fps", type=int, default=int(os.environ.get("FPS","4")))
    p.add_argument("--config", default=os.environ.get("EDGE_CONFIG","smartpole/edge/config.yaml"))
    p.add_argument("--backend", default=os.environ.get("PIPELINE_BACKEND","opencv"))
    p.add_argument("--api_key", default=os.environ.get("API_KEY"))
    p.add_argument("--jwt", default=os.environ.get("JWT_TOKEN"))
    a=p.parse_args()
    if os.path.exists(a.config):
        with open(a.config) as f:
            cfg=yaml.safe_load(f) or {}
            a.server=cfg.get("server_url",a.server); a.iterations=cfg.get("iterations",a.iterations); a.fps=cfg.get("fps",a.fps)
    headers={}
    if a.api_key: headers["x-api-key"]=a.api_key
    if a.jwt: headers["Authorization"]=f"Bearer {a.jwt}"
    hub=SensorHub(); ai=AIPipeline(backend=a.backend)
    for i in range(a.iterations):
        fr=hub.capture(); out=ai.process(fr.data)
        _, jpg = cv2.imencode('.jpg', fr.data)
        image_url=None
        try:
            r=requests.post(f"{a.server}/upload", files={"file":("frame.jpg", jpg.tobytes(), "image/jpeg")}, headers=headers, timeout=5)
            if r.ok: image_url=r.json().get("url")
        except Exception as e: print("[edge] upload failed:", e)
        ev=build_event(fr.timestamp, fr.gps, out, image_url)
        try:
            r=requests.post(f"{a.server}/ingest", json=ev, headers=headers, timeout=5)
            print(f"[edge] {i+1}/{a.iterations} -> {r.status_code} {r.text[:120]}")
        except Exception as e: print("[edge] send failed:", e)
        time.sleep(1.0/max(a.fps,1))

if __name__=="__main__": main()
