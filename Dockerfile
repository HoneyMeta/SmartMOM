# syntax=docker/dockerfile:1
# SmartMOM image: the web UI is built with Node, then served by the Python application.
# The same image also runs the data replayer (python -m replayer), see docker-compose.yml.
#
# Base images and package sources can be replaced, e.g. with a registry mirror:
#   docker build --build-arg NODE_IMAGE=<mirror>/library/node:22-bookworm-slim \
#                --build-arg PYTHON_IMAGE=<mirror>/library/python:3.12-slim-trixie \
#                --build-arg NPM_REGISTRY=<npm registry> --build-arg DEBIAN_MIRROR=<debian mirror> \
#                --build-arg PIP_MIRROR=<pypi index>/simple -t smartmom:local .
ARG NODE_IMAGE=node:22-bookworm-slim
ARG PYTHON_IMAGE=python:3.12-slim-trixie

# ---- 1. web UI ------------------------------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM ${NODE_IMAGE} AS web
# Optional npm registry mirror (empty = registry.npmjs.org)
ARG NPM_REGISTRY=
WORKDIR /src/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund ${NPM_REGISTRY:+--registry "$NPM_REGISTRY"}
COPY web/ ./
RUN npm run build

# ---- 2. runtime -----------------------------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MOM_DATA=/data

# Optional package mirrors (empty = official servers): DEBIAN_MIRROR replaces http://deb.debian.org, e.g.
# http://mirrors.example.org; PIP_MIRROR is a PyPI simple index, e.g. https://pypi.example.org/simple
ARG DEBIAN_MIRROR=
ARG PIP_MIRROR=

# postgresql-client: pg_dump / pg_restore for backups of a PostgreSQL database (same major version as the
# postgres:17 service in docker-compose.yml); tzdata: TZ support; tini: signal handling as PID 1.
RUN if [ -n "$DEBIAN_MIRROR" ]; then sed -i "s|http://deb.debian.org|$DEBIAN_MIRROR|g" /etc/apt/sources.list.d/debian.sources; fi \
 && apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client tzdata tini \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
COPY replayer/requirements.txt /tmp/requirements-replayer.txt
RUN pip install ${PIP_MIRROR:+--index-url "$PIP_MIRROR"} -r /tmp/requirements.txt -r /tmp/requirements-replayer.txt \
 && rm /tmp/requirements*.txt

COPY smartmom/ ./smartmom/
# Deprecated alias package (SmartMOM was formerly HoneyMOM): "python -m honeymom" keeps working for one release.
COPY honeymom/ ./honeymom/
COPY replayer/ ./replayer/
COPY config/llm.example.json ./config/llm.example.json
COPY --from=web /src/web/dist ./web/dist

RUN useradd --system --uid 10001 --gid 0 --home-dir /app --shell /usr/sbin/nologin smartmom \
 && mkdir -p /data \
 && chown -R 10001:0 /data \
 && chmod -R g=u /data

USER 10001
VOLUME ["/data"]
EXPOSE 8900

HEALTHCHECK --interval=15s --timeout=5s --start-period=120s --retries=5 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8900/api/setup/admin', timeout=4); sys.exit(0)"

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "smartmom", "serve", "--http", "8900"]
