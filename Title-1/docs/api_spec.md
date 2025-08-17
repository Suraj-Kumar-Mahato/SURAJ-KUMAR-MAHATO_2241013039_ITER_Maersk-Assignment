# API Spec

## POST /api/v1/measurements
**Headers:** Optional `X-API-KEY`  
**Body (JSON):**
```json
{
  "ts":"2025-08-14T10:20:30Z",
  "device_hash":"<sha256>",
  "tech":"LTE|NR",
  "mcc":"404",
  "mnc":"45",
  "tac":"12345",
  "eci":"0xABCD",
  "pci":"321",
  "earfcn":"1800",
  "nrarfcn":"627334",
  "rsrp": -95.5,
  "rsrq": -10.2,
  "sinr": 12.3,
  "rssi": -60.0,
  "bandwidth":"20MHz",
  "lat": 19.076,
  "lon": 72.8777,
  "extra": { "vendor":"demo" }
}
```
**Responses:** `200 OK {"status":"ok"}`

## GET /api/v1/measurements?limit=100
Returns latest N rows.

## GET /api/v1/geojson
Returns a FeatureCollection for mapping.
