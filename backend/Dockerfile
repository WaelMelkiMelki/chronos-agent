# ─── Builder ─────────────────────────────────────
FROM python:3.12-slim AS builder


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1


WORKDIR /build


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --prefix=/install .


# ─── Runtime ─────────────────────────────────────
FROM python:3.12-slim AS runtime


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:${PATH}"


RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid 1000 --create-home app


COPY --from=builder /install /usr/local


WORKDIR /app
COPY --chown=app:app . .


USER app


EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ─── Development ─────────────────────────────────
FROM runtime AS development


USER root


RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install -e ".[dev]"


USER app


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
