FROM ghcr.io/astral-sh/uv:0.9.7@sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142 AS uv
FROM python:3.12-alpine@sha256:5789aa194f757888f41fa3d48e14b6feaa1b57c0af0b56fcb1372d6474d3bff0 AS builder
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock LICENSE NOTICE ./
COPY flux ./flux
RUN uv sync --locked --no-dev --extra telegram --no-editable

FROM python:3.12-alpine@sha256:5789aa194f757888f41fa3d48e14b6feaa1b57c0af0b56fcb1372d6474d3bff0
ARG SOURCE_REVISION=unreviewed
LABEL org.opencontainers.image.source="https://github.com/hzjanuary/flux-ai-agent" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.revision=$SOURCE_REVISION
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/home/flux
RUN addgroup -g 10001 flux && adduser -D -u 10001 -G flux -h /home/flux flux && \
    mkdir /data && chown flux:flux /data && chmod 0700 /data /home/flux
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY LICENSE NOTICE requirements.lock /app/
COPY docs/release/third-party-licenses.json /app/third-party-licenses.json
USER 10001:10001
VOLUME ["/data"]
ENTRYPOINT ["flux", "--config", "/data/config.json"]
CMD ["doctor"]
