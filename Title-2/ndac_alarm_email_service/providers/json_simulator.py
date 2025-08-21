import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

from .base import ProviderBase

class JSONSimulatorProvider(ProviderBase):
    """
    Reads alarms from a JSON file `json_path` containing a list of alarms.
    Example alarm:
    {
      "timestamp": "2025-08-01T12:00:00Z",
      "alarm_type": "LinkDown",
      "severity": "Critical",
      "network_element": "OLT-12",
      "suggested_action": "Dispatch field tech to site."
    }
    """
    def __init__(self, cfg: dict, logger):
        super().__init__(cfg, logger)
        self.path = cfg.get("json_path") or "sample_data/alarms.json"

    def fetch_alarms(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            self.log.warning("Simulator file not found: %s", self.path)
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Basic validation & normalization
        out = []
        for item in data:
            if not isinstance(item, dict):
                continue
            item.setdefault("suggested_action", "")
            # normalize timestamp
            ts = item.get("timestamp")
            if isinstance(ts, str):
                item["timestamp"] = ts
            else:
                item["timestamp"] = datetime.now(timezone.utc).isoformat()
            out.append(item)
        self.log.info("Fetched %d alarms from simulator", len(out))
        return out
