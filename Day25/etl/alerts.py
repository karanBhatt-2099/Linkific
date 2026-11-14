import smtplib
from email.message import EmailMessage

from etl import config
from etl.logger import get_logger

log = get_logger(__name__)


def send_alert(subject, body):
    """Email the on-call address. Never raises: a broken mail server must not hide the real error."""
    if not (config.SMTP_HOST and config.ALERT_TO):
        log.warning("Email not configured, alert only logged: %s | %s", subject, body)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.ALERT_FROM
    message["To"] = config.ALERT_TO
    message.set_content(body)

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            server.starttls()
            if config.SMTP_USER:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception:
        log.exception("Could not send alert email")
        return False


def notify_failure(context):
    """Airflow on_failure_callback."""
    task = context["task_instance"]
    send_alert(
        f"Airflow task failed: {task.dag_id}.{task.task_id}",
        f"Run: {context.get('run_id')}\nError: {context.get('exception')}",
    )
