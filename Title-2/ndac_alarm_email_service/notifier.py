import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List

import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape

class NotificationError(Exception):
    pass

class Notifier:
    def __init__(self, cfg: dict, logger):
        self.cfg = cfg
        self.log = logger

        self.recipients = cfg.get("recipients") or []
        env_recipients = os.getenv("RECIPIENTS")
        if env_recipients:
            self.recipients = [x.strip() for x in env_recipients.split(",") if x.strip()]

        self.prefer = (cfg.get("notifier", {}).get("prefer") or "smtp").lower()
        self.from_email = cfg.get("notifier", {}).get("from_email") or "ndac-alerts@example.com"

        # templating
        self.env = Environment(
            loader=FileSystemLoader(searchpath="ndac_alarm_service/templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.template = self.env.get_template("email_template.html")

    def _subject(self, alarm: Dict[str, Any]) -> str:
        return f"[NDAC] {alarm.get('severity','?')} - {alarm.get('alarm_type','Alarm')} @ {alarm.get('network_element','?')}"

    def render(self, alarm: Dict[str, Any]) -> (str, str):
        html = self.template.render(alarm=alarm)
        # plaintext fallback
        text = (
            f"NDAC Alarm\\n"
            f"Severity: {alarm.get('severity')}\\n"
            f"Type: {alarm.get('alarm_type')}\\n"
            f"Timestamp: {alarm.get('timestamp')}\\n"
            f"Element: {alarm.get('network_element')}\\n"
            f"Suggested Action: {alarm.get('suggested_action','')}\\n"
        )
        return text, html

    def _smtp_send(self, subject: str, text: str, html: str, recipients: List[str]):
        host = os.getenv("SMTP_HOST") or self.cfg.get("smtp", {}).get("host")
        port = int(os.getenv("SMTP_PORT") or self.cfg.get("smtp", {}).get("port") or 587)
        user = os.getenv("SMTP_USER") or self.cfg.get("smtp", {}).get("username")
        pwd  = os.getenv("SMTP_PASS") or self.cfg.get("smtp", {}).get("password")
        use_tls = (os.getenv("SMTP_TLS") or str(self.cfg.get("smtp", {}).get("use_tls", "true"))).lower() == "true"

        if not (host and user and pwd):
            raise NotificationError("SMTP not configured (host/user/pass)")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = ", ".join(recipients)

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP(host, port, timeout=15)
            if use_tls:
                server.starttls()
            server.login(user, pwd)
            server.sendmail(self.from_email, recipients, msg.as_string())
            server.quit()
        except Exception as e:
            raise NotificationError(f"SMTP send failed: {e}")

    def _sendgrid_send(self, subject: str, text: str, html: str, recipients: List[str]):
        key = os.getenv("SENDGRID_API_KEY") or self.cfg.get("sendgrid", {}).get("api_key")
        if not key:
            raise NotificationError("SendGrid API key not configured")

        data = {
            "personalizations": [{"to": [{"email": r} for r in recipients]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text},
                {"type": "text/html", "value": html},
            ],
        }
        try:
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=data,
                timeout=15,
            )
            if resp.status_code >= 300:
                raise NotificationError(f"SendGrid error {resp.status_code}: {resp.text}")
        except requests.RequestException as e:
            raise NotificationError(f"SendGrid send failed: {e}")

    def send_alarm(self, alarm: Dict[str, Any]):
        if not self.recipients:
            raise NotificationError("No recipients configured")

        text, html = self.render(alarm)
        subject = self._subject(alarm)

        # Simple retry with jitter
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                if self.prefer == "sendgrid":
                    self._sendgrid_send(subject, text, html, self.recipients)
                else:
                    self._smtp_send(subject, text, html, self.recipients)
                self.log.info("Email sent: %s -> %s", subject, self.recipients)
                return
            except NotificationError as e:
                if attempt == max_attempts:
                    raise
                sleep = (2 ** attempt) + (attempt * 0.3)
                self.log.warning("Attempt %d failed: %s; retrying in %.1fs", attempt, e, sleep)
                time.sleep(sleep)
