FROM python:latest

COPY . .
RUN pip install -r requirements.txt

ENV GREETING="Hello from a container!"
ENV SECRET_KEY="super-secret-123"

CMD gunicorn --bind 0.0.0.0:8000 app:app
