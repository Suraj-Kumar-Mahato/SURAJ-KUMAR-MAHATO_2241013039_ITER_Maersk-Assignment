from typing import List, Dict, Any

class ProviderBase:
    """Base class for alarm providers."""
    def __init__(self, cfg: dict, logger):
        self.cfg = cfg
        self.log = logger

    def fetch_alarms(self) -> List[Dict[str, Any]]:
        """Return a list of alarm dicts. Must be implemented by subclasses."""
        raise NotImplementedError
