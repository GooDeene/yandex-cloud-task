ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base

ENV BACKEND_VERSION=${PYTHON_VERSION}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV YDB_ENDPOINT='grpcs://ydb.serverless.yandexcloud.net:2135'
ENV YDB_DATABASE='/ru-central1/b1g5oo97dli38aeou60r/etn85iol43qfi7epup90'

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


USER appuser

COPY . .

EXPOSE 8000

CMD gunicorn 'main:app' --bind=0.0.0.0:8000
