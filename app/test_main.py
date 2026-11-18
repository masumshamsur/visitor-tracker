from unittest.mock import patch

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_home_serves_web_page():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "visitor-tracker" in res.text


@patch.object(main.cache, "incr", return_value=42)
def test_visit_counts_visits(_):
    body = client.post("/api/visit").json()
    assert body["visits"] == 42
    assert body["pod"]


@patch.object(main.cache, "incr", side_effect=main.redis.ConnectionError)
def test_visit_degrades_without_redis(_):
    assert client.post("/api/visit").json()["visits"] == -1


@patch.object(main.cache, "ping", side_effect=main.redis.ConnectionError)
def test_readyz_fails_without_redis(_):
    assert client.get("/readyz").status_code == 503


def test_metrics_exposed():
    assert "app_requests_total" in client.get("/metrics").text
