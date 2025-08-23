FROM python:3.12-slim

# Optional: install system deps you need
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash tini && \
    rm -rf /var/lib/apt/lists/*

# Debug adapter
RUN pip install --no-cache-dir debugpy requests

# Non-root
RUN useradd -ms /bin/bash dev
USER dev

WORKDIR /work

# Entrypoint wrapper to start debugpy then your target
COPY --chown=dev:dev entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
