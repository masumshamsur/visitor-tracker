# Build from the project root:  docker build -t visitor-tracker .
# ---- build stage ----
FROM python:3.12-slim AS build
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime stage ----
FROM python:3.12-slim
RUN useradd --uid 10001 --create-home appuser
WORKDIR /app
COPY --from=build /install /usr/local
COPY app/main.py .
COPY app/static/ static/
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
