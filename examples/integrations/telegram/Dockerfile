FROM python:3.10.4 AS base

FROM base AS builder

WORKDIR /app

RUN groupadd -r app && useradd -d /app -r -g app app \
    && chown app:app -R /app

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

COPY --chown=app:app ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

USER app


FROM builder AS dev

COPY --chown=app:app . /app
