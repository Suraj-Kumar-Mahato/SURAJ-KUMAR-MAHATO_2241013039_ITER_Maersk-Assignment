# NDAC Alarm Email Notification Service

A production-ready, assessment-friendly backend that monitors alarms from **NDAC (Nokia Digital Access Cloud)** (or a simulator)
and sends **email notifications** to stakeholders for **Critical** and **Major** severities.

## ✨ Uniqueness & Highlights
- **Pluggable data source**: real NDAC REST API or a JSON simulator.
- **Idempotent alerts**: dedupe via stable alarm **digest** stored in **SQLite**.
- **Config-first**: `config.yaml` with **env overrides** for secrets and CI/CD.
- **Robust delivery**: exponential **retry with jitter**, failure logging.
- **Templated emails**: Jinja2 HTML + plaintext fallback.
- **Dry-run mode**: exercise the full pipeline without sending emails.
- **Dockerized**: one-command container run; also works as a simple script or service.
- **Explainable**: small, readable modules with key comments and a clear flow.

## 🧱 Architecture
```
[NDAC / Simulator] -> [Poller] -> [Filter (Critical/Major)] -> [Dedupe/SQLite]
                                                   |-> [Render Template] -> [SMTP/SendGrid] -> Stakeholders
                                                   '--> [Logging + Retry]
```
- Poll interval is **configurable** (default 3600 seconds).
- The service stores last processed timestamps and hashes to prevent duplicate emails.

## 📦 Repo Layout
```
ndac-alarm-email-service/
├── main.py
├── config.yaml
├── requirements.txt
├── .env.example
├── Dockerfile
├── README.md
├── sample_data/
│   └── alarms.json
└── ndac_alarm_service/
    ├── __init__.py
    ├── config.py
    ├── logger.py
    ├── storage.py
    ├── notifier.py
    ├── templates/
    │   └── email_template.html
    └── providers/
        ├── base.py
        ├── json_simulator.py
        └── ndac_api.py     # placeholder for real NDAC integration
```

## ⚙️ Quick Start (Local)
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy env template and set secrets
cp .env.example .env
# Edit .env to set SMTP credentials or SENDGRID_API_KEY

# Dry run (no emails sent)
python main.py --dry-run --once

# Real run (sends emails if configured)
python main.py
```

## 🐳 Docker
```bash
docker build -t ndac-alarm-service .
docker run --env-file .env -v $(pwd)/sample_data:/app/sample_data ndac-alarm-service
```

## 🔐 Config (config.yaml)
- `provider.type`: `"json"` for simulator, `"ndac_api"` for real integration
- `poll_interval_seconds`: how often to poll (default 3600)
- `severity_filter`: `["Critical","Major"]`
- `recipients`: list of email addresses
- `smtp` or `sendgrid` settings (can be provided via env)

### Env Overrides (recommended for secrets)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_TLS`
- `SENDGRID_API_KEY`
- `RECIPIENTS` (comma-separated)

## 🧪 Sample Data
`sample_data/alarms.json` contains synthetic alarms. Modify or stream new events to simulate live updates.

## 🧰 CLI
```
python main.py              # run forever (poll loop)
python main.py --once       # single poll & process cycle
python main.py --dry-run    # don't send emails
python main.py --interval 300
```

## 📚 Key Points (Explain to Reviewers)
1. **Provider pattern** cleanly separates data collection from notification.
2. **SQLite** keeps a persistent trail: last processed time + sent digests.
3. **Template-driven** emails make content consistent and branded.
4. **Retry with jitter** prevents thundering herd and improves robustness.
5. **Config + env** makes it portable to GitHub Actions, Docker, or on-prem.

## 📄 License
MIT
