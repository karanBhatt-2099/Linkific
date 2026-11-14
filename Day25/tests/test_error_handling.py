"""Tests for retry logic, email alerts and error recovery."""
from types import SimpleNamespace

import pytest

from etl import alerts, config, pipeline, quality
from etl.retry import retry
from tests.conftest import AS_OF
from tests.fake_sink import FakeSink


# ---------- retry ----------
def test_retry_succeeds_after_temporary_failures():
    calls = {"n": 0}

    @retry(times=3, delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("temporary")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3


def test_retry_gives_up_and_raises():
    calls = {"n": 0}

    @retry(times=3, delay=0)
    def always_fails():
        calls["n"] += 1
        raise ValueError("down")

    with pytest.raises(ValueError):
        always_fails()
    assert calls["n"] == 3


def test_retry_ignores_other_exception_types():
    calls = {"n": 0}

    @retry(times=3, delay=0, exceptions=(KeyError,))
    def wrong_error():
        calls["n"] += 1
        raise ValueError("not retried")

    with pytest.raises(ValueError):
        wrong_error()
    assert calls["n"] == 1


# ---------- email alerts ----------
class FakeSMTP:
    sent = []
    fail = False

    def __init__(self, host, port, timeout=None):
        if FakeSMTP.fail:
            raise OSError("mail server down")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, message):
        FakeSMTP.sent.append(message)


@pytest.fixture
def mail(monkeypatch):
    FakeSMTP.sent, FakeSMTP.fail = [], False
    monkeypatch.setattr(config, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(config, "ALERT_TO", "oncall@test")
    monkeypatch.setattr(alerts.smtplib, "SMTP", FakeSMTP)
    return FakeSMTP


def test_alert_is_emailed(mail):
    assert alerts.send_alert("Subject line", "Body text") is True
    assert mail.sent[0]["Subject"] == "Subject line"
    assert mail.sent[0]["To"] == "oncall@test"


def test_alert_without_smtp_settings_is_only_logged(monkeypatch):
    monkeypatch.setattr(config, "SMTP_HOST", "")
    assert alerts.send_alert("s", "b") is False


def test_alert_never_raises_when_mail_server_is_down(mail):
    mail.fail = True
    assert alerts.send_alert("s", "b") is False


def test_airflow_failure_callback_builds_alert(monkeypatch):
    sent = []
    monkeypatch.setattr(alerts, "send_alert", lambda subject, body: sent.append((subject, body)))
    task = SimpleNamespace(dag_id="hospital_etl", task_id="load")
    alerts.notify_failure({"task_instance": task, "run_id": "r1", "exception": "boom"})
    assert "hospital_etl.load" in sent[0][0]
    assert "boom" in sent[0][1]


# ---------- error recovery in the pipeline ----------
def test_failed_load_keeps_watermark_and_next_run_recovers(spark, workspace, monkeypatch):
    source, staging = workspace
    alerts_sent = []
    monkeypatch.setattr(pipeline, "send_alert", lambda subject, body: alerts_sent.append(subject))
    sink = FakeSink()

    sink.fail_upserts = True
    with pytest.raises(RuntimeError, match="outage"):
        pipeline.run_pipeline(spark, sink, source, staging, as_of=AS_OF)
    assert sink.watermarks == {}          # nothing marked as loaded
    assert sink.rows("FACT_APPOINTMENTS") == []
    assert len(alerts_sent) == 1          # on-call was told

    sink.fail_upserts = False
    pipeline.run_pipeline(spark, sink, source, staging, as_of=AS_OF)
    assert len(sink.rows("FACT_APPOINTMENTS")) == 13   # same rows are picked up again
    assert "FACT_APPOINTMENTS" in sink.watermarks


def test_too_many_rejected_rows_stops_the_run_before_loading(spark, workspace, monkeypatch):
    source, staging = workspace
    alerts_sent = []
    monkeypatch.setattr(pipeline, "send_alert", lambda subject, body: alerts_sent.append(subject))
    monkeypatch.setattr(config, "MAX_REJECT_RATIO", 0.1)
    sink = FakeSink()

    with pytest.raises(quality.DataQualityError):
        pipeline.run_pipeline(spark, sink, source, staging, as_of=AS_OF)
    assert sink.tables == {}
    assert len(alerts_sent) == 1
