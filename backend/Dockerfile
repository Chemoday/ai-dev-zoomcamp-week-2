FROM python:3.10-slim

# Official uv binary, no pip bootstrap needed.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

EXPOSE 8000

# Shell form so ${PORT} expands - Render (and similar PaaS) inject PORT
# and require the container to listen on it; defaults to 8000 for
# docker-compose / plain `docker run`, where PORT isn't set.
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
