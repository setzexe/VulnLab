FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

RUN addgroup --system vulnlab \
    && adduser --system --ingroup vulnlab vulnlab

COPY --chown=vulnlab:vulnlab . .

RUN mkdir -p /app/instance \
    && chown -R vulnlab:vulnlab /app/instance

USER vulnlab

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--no-control-socket", "--error-logfile", "-", "run:app"]