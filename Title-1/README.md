# LTE/5G Coverage & KPI Testing Platform (Android + Cloud)

A mobile + cloud platform for LTE/5G coverage and KPI testing tailored for private cellular networks in industrial environments (e.g., container terminals). 
Target stakeholder: APM Terminals IT & operations teams.

**Uniqueness**: 
- Offline-first data capture with retry + file-backed queue
- Privacy-preserving hashing for device IDs (salted SHA-256)
- Pluggable metric adapters for LTE/NR (future vendor APIs like QXDM)
- One-command backend (Docker) + built-in dashboard (Leaflet + Chart.js)
- Simulator to generate realistic demo data

## Quick Start

### 1) Backend (Flask + SQLite)
**Option A — Docker (recommended)**
```bash
docker compose up --build
```
The API will be at `http://localhost:5000`, dashboard at `http://localhost:5000/dashboard`.

**Option B — Local Python**
```bash
cd backend
python -m venv venv && source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
# Create a .env (optional): API_KEY=your_key_here
python app.py
```

### 2) Android App
- Open `android-app/` in Android Studio (Arctic Fox or newer).
- Set `BASE_URL` in `ApiClient.kt` to your backend address (e.g., http://10.0.2.2:5000 for emulator).
- Run on a device (preferred) with SIM or connected to a 5G/LTE network. Grant permissions when prompted.

### 3) Demo Without a Device
- Run the data simulator:
```bash
python tools/simulator.py --api http://localhost:5000 --api-key devkey
```
- Open the dashboard: `http://localhost:5000/dashboard`

## Project Structure
```
LTE5G-Coverage-KPI-Testing-Platform/
├── android-app/              # Kotlin app (TelephonyManager + Location + HTTP posting)
├── backend/                  # Flask API, SQLite, Leaflet + Chart.js dashboard
├── tools/                    # Data generator / simulator
├── docs/                     # Architecture, API spec, uniqueness
├── docker-compose.yml
├── LICENSE
└── README.md
```

## Key Components & Flow
1. **Android app** captures KPIs (RSRP, RSRQ, SINR, bands, cell IDs) + GPS.
2. Data is **hashed** for privacy (device IDs) and **queued** if offline.
3. Backend **ingests** JSON, persists to **SQLite**, exposes **GeoJSON**.
4. Dashboard **maps** points (Leaflet) and **charts** trends (Chart.js).

## API Quick Reference
- `POST /api/v1/measurements` (JSON body) – ingest a datum
- `GET  /api/v1/measurements` – list latest (paginated)
- `GET  /api/v1/geojson` – map-ready features
- `GET  /dashboard` – web UI

See `docs/api_spec.md` for full details.

## Security
- Optional **API key** via `X-API-KEY` header (set `API_KEY` in `.env`). 
- CORS disabled by default; enable carefully for your deployment.
- Device identifiers are salted and hashed on-device before upload.

## License
MIT — use freely with attribution.
