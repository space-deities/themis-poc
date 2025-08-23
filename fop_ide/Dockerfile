# Theia IDE with Python extensions baked in
FROM ghcr.io/eclipse-theia/theia-ide/theia-ide:1.64.100

# 1) OS deps + Python + ripgrep (Theia uses rg) + unzip + curl + npm (already in base)
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip ripgrep unzip curl \
 && rm -rf /var/lib/apt/lists/*

# 2) Project-wide Python venv + common dev tools
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir -U pip setuptools wheel \
 && /opt/venv/bin/pip install --no-cache-dir debugpy black ruff

ENV PATH="/opt/venv/bin:${PATH}"

# 3) Download and preinstall VSIX from Open VSX with `ovsx`
#    (The default registry is open-vsx.org; --registryUrl not required, but shown for clarity)
RUN npm i -g ovsx@0.10.x \
 && mkdir -p /home/theia/.theia-ide/deployedPlugins /home/project \
 && cd /home/theia/.theia-ide/deployedPlugins \
 && export OVSX_REGISTRY_URL="https://open-vsx.org" \
 && for ext in \
      ms-python.python \
      ms-python.vscode-pylance \
      ms-toolsai.jupyter \
      ms-python.debugpy \
      ms-pyright.pyright \
    ; do \
      ovsx get "$ext" -o "$ext.vsix"; \
      unzip -q "$ext.vsix" -d "$ext-raw"; \
      # 'extension' is the payload; link that as the plugin root
      if [ -d "$ext-raw/extension" ]; then \
        ln -s "$ext-raw/extension" "$ext"; \
      else \
        ln -s "$ext-raw" "$ext"; \
      fi; \
      # Optional: silence l10n warnings seen in logs for some builds
      mkdir -p "$ext/l10n"; \
      rm -f "$ext.vsix"; \
    done \
 && chown -R theia:theia /home/theia/.theia-ide /home/project /opt/venv

# 4) Make Theia load plugins from our preinstalled folder (note the triple slash)
ENV THEIA_DEFAULT_PLUGINS="local-dir:///home/theia/.theia-ide/deployedPlugins"

# Keep container defaults (the base image starts Theia)
USER theia
EXPOSE 3000
