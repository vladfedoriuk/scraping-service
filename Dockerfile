FROM python:3.10.4 AS base

FROM base as builder

# either 'development' or 'production'
ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.1.13 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

WORKDIR /code

RUN groupadd -r web && useradd -d /code -r -g web web \
  && chown web:web -R /code \
  && mkdir -p /var/www/django/static /var/www/django/media \
  && chown web:web /var/www/django/static /var/www/django/media

COPY --chown=web:web ./poetry.lock ./pyproject.toml /code/

RUN pip install "poetry==$POETRY_VERSION"

# Project initialization:
RUN echo "$DJANGO_ENV" && poetry version \
  && poetry run pip install -U pip \
  && poetry install \
    $(if [ "$DJANGO_ENV" = 'production' ]; then echo '--no-dev'; fi) \
    --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && if [ "$DJANGO_ENV" = 'production' ]; then rm -rf "$POETRY_CACHE_DIR"; fi

USER web

FROM builder as dev

ENV DEBUG 1
ENV DJANGO_SETTINGS_MODULE 'scraping.settings.dev'
COPY . /code
