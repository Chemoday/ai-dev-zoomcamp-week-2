FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Shell form so ${PORT} expands - Render (and similar PaaS) inject PORT
# and require the container to listen on it; defaults to 8000 for
# docker-compose / plain `docker run`, where PORT isn't set.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
