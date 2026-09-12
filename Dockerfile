FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

RUN addgroup --system vulnlab \
    && adduser --system --ingroup vulnlab vulnlab

COPY --chown=vulnlab:vulnlab . .

RUN mkdir -p /app/instance \
    && chown -R vulnlab:vulnlab /app/instance

USER vulnlab

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "run", "run", "--host=0.0.0.0", "--port=5000"]