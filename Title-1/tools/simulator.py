import requests, random, time, argparse, json
from datetime import datetime, timezone
import hashlib, os

def hash_device_id(device_id, salt='demo-salt'):
    return hashlib.sha256((salt + device_id).encode()).hexdigest()

def gen_point(center=(19.0760,72.8777), spread_km=5):
    # rough jitter
    lat, lon = center
    dlat = (random.random()-0.5) * (spread_km/110.0)
    dlon = (random.random()-0.5) * (spread_km/110.0)
    return lat+dlat, lon+dlon

def gen_measurement(device_id='demo-device', tech='LTE'):
    lat, lon = gen_point()
    rsrp = random.uniform(-120, -70)
    rsrq = random.uniform(-20, -3)
    sinr = random.uniform(-5, 30)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "device_hash": hash_device_id(device_id),
        "tech": tech,
        "mcc": "404", "mnc": "45",
        "tac": "12345", "eci": "0xABCD", "pci": "321",
        "earfcn": "1800", "nrarfcn": None,
        "rsrp": round(rsrp,2), "rsrq": round(rsrq,2), "sinr": round(sinr,2),
        "rssi": None, "bandwidth": "10MHz",
        "lat": lat, "lon": lon,
        "extra": {"note":"simulated"}
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--api', default='http://localhost:5000')
    ap.add_argument('--api-key', default='')
    ap.add_argument('--count', type=int, default=200)
    args = ap.parse_args()

    headers = {}
    if args.api_key:
        headers['X-API-KEY'] = args.api_key

    for i in range(args.count):
        tech = 'NR' if i % 3 == 0 else 'LTE'
        m = gen_measurement(tech=tech)
        r = requests.post(f"{args.api}/api/v1/measurements", json=m, headers=headers, timeout=5)
        print(i, r.status_code, r.text)
        time.sleep(0.05)
