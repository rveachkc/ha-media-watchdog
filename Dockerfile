FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

COPY dist/*.whl /app/
RUN pip install --no-cache-dir /app/*.whl

ENTRYPOINT ["ha-media-watchdog"]
