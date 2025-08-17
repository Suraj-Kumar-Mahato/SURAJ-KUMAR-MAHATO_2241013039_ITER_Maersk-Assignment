import os, json, time, hashlib
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
# CORS(app)  # Enable cautiously if needed

os.makedirs('data', exist_ok=True)
DB_URL = 'sqlite:///data/measurements.sqlite'
engine = create_engine(DB_URL, echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)

# Create table
with engine.begin() as conn:
    conn.execute(text("""            CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            device_hash TEXT,
            tech TEXT,
            mcc TEXT,
            mnc TEXT,
            tac TEXT,
            eci TEXT,
            pci TEXT,
            earfcn TEXT,
            nrarfcn TEXT,
            rsrp REAL,
            rsrq REAL,
            sinr REAL,
            rssi REAL,
            bandwidth TEXT,
            lat REAL,
            lon REAL,
            extra JSON
        );
    """))

API_KEY = os.getenv('API_KEY')

def require_api_key():
    if API_KEY:
        key = request.headers.get('X-API-KEY')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
    return None

@app.get('/')
def root():
    return jsonify({'status':'ok','dashboard':'/dashboard'})

@app.post('/api/v1/measurements')
def ingest():
    unauthorized = require_api_key()
    if unauthorized: return unauthorized
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'error':'Invalid JSON'}), 400

    required = ['ts','device_hash','tech','lat','lon']
    if not all(k in data for k in required):
        return jsonify({'error':'Missing required fields'}), 400

    with engine.begin() as conn:
        conn.execute(text("""                INSERT INTO measurements (
                ts, device_hash, tech, mcc, mnc, tac, eci, pci, earfcn, nrarfcn,
                rsrp, rsrq, sinr, rssi, bandwidth, lat, lon, extra
            ) VALUES (
                :ts, :device_hash, :tech, :mcc, :mnc, :tac, :eci, :pci, :earfcn, :nrarfcn,
                :rsrp, :rsrq, :sinr, :rssi, :bandwidth, :lat, :lon, :extra
            )
        """), {
            'ts': data.get('ts'),
            'device_hash': data.get('device_hash'),
            'tech': data.get('tech'),
            'mcc': data.get('mcc'),
            'mnc': data.get('mnc'),
            'tac': data.get('tac'),
            'eci': data.get('eci'),
            'pci': data.get('pci'),
            'earfcn': data.get('earfcn'),
            'nrarfcn': data.get('nrarfcn'),
            'rsrp': data.get('rsrp'),
            'rsrq': data.get('rsrq'),
            'sinr': data.get('sinr'),
            'rssi': data.get('rssi'),
            'bandwidth': data.get('bandwidth'),
            'lat': data.get('lat'),
            'lon': data.get('lon'),
            'extra': json.dumps(data.get('extra', {}))
        })
    return jsonify({'status':'ok'})

@app.get('/api/v1/measurements')
def list_measurements():
    unauthorized = require_api_key()
    if unauthorized: return unauthorized
    limit = int(request.args.get('limit', 100))
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM measurements ORDER BY id DESC LIMIT :limit"), {'limit': limit}).mappings().all()
        return jsonify([dict(r) for r in rows])

@app.get('/api/v1/geojson')
def geojson():
    unauthorized = require_api_key()
    if unauthorized: return unauthorized
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM measurements ORDER BY id DESC LIMIT 5000")).mappings().all()
    features = []
    for r in rows:
        props = dict(r)
        for k in ['lat','lon','id']:
            props.pop(k, None)
        features.append({
            'type':'Feature',
            'geometry': {'type':'Point','coordinates':[r['lon'], r['lat']]},
            'properties': props
        })
    return jsonify({'type':'FeatureCollection','features':features})

@app.get('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.get('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
