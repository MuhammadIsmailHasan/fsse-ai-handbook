# ⚠️ A naive "it works on my machine" Dockerfile. Improve it — see README.md.
FROM python:latest

WORKDIR /app
COPY . .
RUN pip install flask flask-sqlalchemy "psycopg[binary]" gunicorn

ENV JWT_SECRET_KEY=super-secret-key-change-in-production
EXPOSE 5091
CMD flask --app wsgi run --host 0.0.0.0 --port 5091
