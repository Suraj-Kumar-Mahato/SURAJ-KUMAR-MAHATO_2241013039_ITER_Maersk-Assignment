import os
import re
import yaml

ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")

def _env_expand(value: str) -> str:
    def repl(m):
        return os.getenv(m.group(1), "")
    return ENV_PATTERN.sub(repl, value)

def _walk_env_expand(obj):
    if isinstance(obj, dict):
        return {k: _walk_env_expand(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk_env_expand(v) for v in obj]
    if isinstance(obj, str):
        return _env_expand(obj)
    return obj

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # allow env var overrides
    cfg = _walk_env_expand(cfg)

    # recipients via env (comma-separated)
    env_recipients = os.getenv("RECIPIENTS")
    if env_recipients:
        cfg["recipients"] = [x.strip() for x in env_recipients.split(",") if x.strip()]

    # notifier preference via env
    prefer = os.getenv("NOTIFIER_PREFER")
    if prefer:
        cfg.setdefault("notifier", {})["prefer"] = prefer

    return cfg
