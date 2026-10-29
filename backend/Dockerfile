FROM python:3.12-slim AS base

WORKDIR /app

# System deps: none needed beyond what pip wheels bring in.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user — standard container hardening.
RUN useradd --create-home --shell /bin/false scanner
USER scanner

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
