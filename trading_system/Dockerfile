FROM gmag11/metatrader5_vnc:latest

COPY . /app
WORKDIR /app

# ===================================================================
# SYSTEM DEPENDENCIES + PYTHON PACKAGES
# ===================================================================
RUN mkdir -p /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    chmod 644 /etc/apt/keyrings/winehq-archive.key && \
    apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    ln -sf /usr/bin/python3 /usr/bin/python || true && \
    rm -rf /var/lib/apt/lists/*

# CRITICAL: Install rpyc inside Wine Python (MetaTrader5 lives here)
RUN wine /root/.wine/drive_c/Python/Python311/python.exe -m pip install rpyc --no-deps || true

# Copy RPyC server
COPY rpyc_mt5_server.py /app/rpyc_mt5_server.py

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

VOLUME ["/config"]
RUN mkdir -p /app/data/historical /app/models /app/logs && chmod -R 777 /app

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]