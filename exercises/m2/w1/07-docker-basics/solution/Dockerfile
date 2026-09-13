FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# GREETING and any secrets are provided at runtime: docker run -e GREETING=...
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
