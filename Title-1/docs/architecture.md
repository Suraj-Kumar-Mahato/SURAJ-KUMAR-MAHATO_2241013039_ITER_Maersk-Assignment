# Architecture Overview

- **Android Client** (Kotlin): Collects KPIs via `TelephonyManager` and location via `FusedLocationProvider`. 
  - Hashes device identifiers with salt.
  - Queues payload to disk if offline; retries with backoff.
  - Configurable base URL + API key.
- **Backend** (Flask + SQLite): Ingests JSON, persists, exposes list/geojson endpoints, serves dashboard.
- **Dashboard**: Leaflet map for coverage points; Chart.js for RSRP/RSRQ/SINR trends.
- **Simulator**: Generates realistic data for demos and tests.
