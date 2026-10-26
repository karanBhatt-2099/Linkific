import smtplib
from email.message import EmailMessage

from src import config
from src.utils.logger import get_logger

log = get_logger("alerts")


def send_failure_email(subject: str, body: str) -> None:
    """Send an email when the pipeline fails. Does nothing if alerts are disabled."""
    if not config.ALERT_EMAIL_ENABLED:
        log.info("Email alerts disabled, skipping alert: %s", subject)
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = config.SMTP_USER
        msg["To"] = config.ALERT_TO
        msg.set_content(body)
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        log.info("Alert email sent to %s", config.ALERT_TO)
    except Exception as exc:  # never let the alert itself crash the pipeline
        log.error("Could not send alert email: %s", exc)
