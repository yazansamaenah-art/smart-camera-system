import os, uuid, time as _t, datetime as dt
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from .db import init_db, SessionLocal
from .models import Event
from .schemas import EventIn
from .policy.engine import load_rules, apply_policy
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

POLICY_FILE=os.getenv('POLICY_FILE','cloud/policy/rules.yaml')
API_KEY=os.getenv('API_KEY'); JWT_SECRET=os.getenv('JWT_SECRET')
BLOBS_DIR=os.getenv('BLOBS_DIR','blobs')
S3_BUCKET=os.getenv('S3_BUCKET'); GCS_BUCKET=os.getenv('GCS_BUCKET')

app=FastAPI(title='SmartPole Cloud API', version='0.3.0')
INGEST_COUNT = Counter("smartpole_ingest_total", "Total ingested events", ["type"])
INGEST_LATENCY = Histogram("smartpole_ingest_latency_seconds", "Ingest latency")

rules_cache=None; rules_mtime=0.0
def get_rules():
    global rules_cache, rules_mtime
    try:
        m=os.path.getmtime(POLICY_FILE)
        if rules_cache is None or m!=rules_mtime:
            rules_cache=load_rules(POLICY_FILE); rules_mtime=m
    except FileNotFoundError: rules_cache={}
    return rules_cache

def require_auth(x_api_key: str|None = Header(default=None), authorization: str|None = Header(default=None)):
    if API_KEY and x_api_key==API_KEY: return True
    if JWT_SECRET and authorization and authorization.lower().startswith('bearer '):
        import jwt
        token=authorization.split(' ',1)[1]
        try: jwt.decode(token, JWT_SECRET, algorithms=['HS256']); return True
        except Exception: pass
    if not API_KEY and not JWT_SECRET: return True
    raise HTTPException(status_code=401, detail='Unauthorized')

@app.on_event('startup')
def startup():
    init_db(); os.makedirs(BLOBS_DIR, exist_ok=True)

@app.get('/health')
def health(): return {'ok':True}

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def _store_local(data, name):
    path=os.path.join(BLOBS_DIR,name); open(path,'wb').write(data); return f'/blobs/{name}'
def _store_s3(data, name):
    import boto3; s3=boto3.client('s3'); s3.put_object(Bucket=S3_BUCKET, Key=name, Body=data, ContentType='image/jpeg'); return f's3://{S3_BUCKET}/{name}'
def _store_gcs(data, name):
    from google.cloud import storage; client=storage.Client(); bucket=client.bucket(GCS_BUCKET); blob=bucket.blob(name); blob.upload_from_string(data, content_type='image/jpeg'); return f'gs://{GCS_BUCKET}/{name}'

@app.post('/upload')
def upload(file: UploadFile = File(...), _: bool = Depends(require_auth)):
    data=file.file.read(); name=f'{uuid.uuid4().hex}.jpg'
    if S3_BUCKET: url=_store_s3(data,name)
    elif GCS_BUCKET: url=_store_gcs(data,name)
    else: url=_store_local(data,name)
    return {'url':url}

@app.post('/ingest')
def ingest(event: EventIn, _: bool = Depends(require_auth)):
    start = _t.time()
    rules=get_rules(); data=event.model_dump()
    filt=apply_policy(data, rules)
    if filt is None: return {'status':'dropped_by_policy'}
    db=SessionLocal()
    try:
        e=Event(type=filt['type'], lat=filt['location']['lat'], lon=filt['location']['lon'], payload=filt['payload'], source=filt.get('source','edge'))
        db.add(e); db.commit(); db.refresh(e)
        INGEST_COUNT.labels(filt['type']).inc()
        INGEST_LATENCY.observe(_t.time() - start)
        return {'status':'ok','id':e.id}
    finally: db.close()

@app.post('/ingest/message')
def ingest_message(msg: dict, _: bool = Depends(require_auth)):
    payload = msg.get('event', msg)
    try:
        event = EventIn(**payload)
    except Exception as e:
        raise HTTPException(400, f'Invalid payload: {e}')
    return ingest(event)

@app.get('/events')
def events(limit:int=50):
    db=SessionLocal()
    try:
        rows=db.execute(select(Event).order_by(Event.id.desc()).limit(limit)).scalars().all()
        return [{'id':r.id,'type':r.type,'location':{'lat':r.lat,'lon':r.lon},'payload':r.payload} for r in rows]
    finally: db.close()

@app.get('/analytics/counts')
def counts():
    db = SessionLocal()
    try:
        total = db.execute(select(func.count(Event.id))).scalar()
        rows = db.execute(select(Event.type, func.count()).group_by(Event.type)).all()
        return {'total': total, 'by_type': dict(rows)}
    finally:
        db.close()

@app.get('/analytics/last24h')
def last24h():
    db = SessionLocal()
    try:
        cutoff = dt.datetime.utcnow() - dt.timedelta(hours=24)
        res = db.execute(select(func.count(Event.id)).where(Event.timestamp >= cutoff)).scalar()
        return {'since': cutoff.isoformat()+'Z', 'count': res}
    finally:
        db.close()

@app.get('/', response_class=HTMLResponse)
def dashboard():
    html = """<html><head><title>SmartPole Dashboard</title>
    <style>body{font-family:Arial;margin:20px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:6px}img{max-height:120px}</style>
    </head><body>
    <h2>SmartPole Events</h2>
    <div>Filter: <select id='type'><option value=''>all</option><option>presence</option><option>traffic_violation</option><option>air_quality</option></select>
    <button onclick='loadEvents()'>Refresh</button></div>
    <table id='tbl'><thead><tr><th>ID</th><th>Type</th><th>Location</th><th>Payload</th><th>Image</th></tr></thead><tbody></tbody></table>
    <script>
    async function loadEvents(){const r=await fetch('/events');const data=await r.json();const t=document.getElementById('type').value;const tb=document.querySelector('#tbl tbody');tb.innerHTML='';data.filter(e=>!t||e.type===t).forEach(e=>{const tr=document.createElement('tr');const img=e.payload&&e.payload.image_url?`<img src='${e.payload.image_url}'/>`:'';tr.innerHTML=`<td>${e.id}</td><td>${e.type}</td><td>${e.location.lat.toFixed(5)},${e.location.lon.toFixed(5)}</td><td><pre>${JSON.stringify(e.payload,null,2)}</pre></td><td>${img}</td>`;tb.appendChild(tr);});}
    loadEvents(); setInterval(loadEvents,3000);
    </script></body></html>"""
    return HTMLResponse(content=html)

app.mount('/blobs', StaticFiles(directory=BLOBS_DIR), name='blobs')
