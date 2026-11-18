"""Cloud-native visit counter: web UI + JSON API (FastAPI + Redis + Prometheus)."""
import os
import socket
from pathlib import Path

import redis
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
APP_VERSION = os.getenv("APP_VERSION", "dev")
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="visitor-tracker", version=APP_VERSION)
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)

REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["endpoint"])


@app.get("/", include_in_schema=False)
def home():
    """Browser interface."""
    REQUESTS.labels(endpoint="/").inc()
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/visit")
def visit():
    """Record a visit and report which pod served it."""
    REQUESTS.labels(endpoint="/api/visit").inc()
    try:
        visits = cache.incr("visits")
    except redis.RedisError:
        visits = -1  # degrade gracefully if Redis is down
    return {"message": "Hello from visitor-tracker", "visits": visits,
            "pod": socket.gethostname(), "version": APP_VERSION}


@app.get("/healthz")
def healthz():
    """Liveness probe: process is up."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz(response: Response):
    """Readiness probe: dependencies reachable."""
    try:
        cache.ping()
        return {"status": "ready"}
    except redis.RedisError:
        response.status_code = 503
        return {"status": "redis unavailable"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
