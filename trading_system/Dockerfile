FROM gmag11/metatrader5_vnc:latest

# Copy your entire trading system
COPY . /app
WORKDIR /app

# ===================================================================
# SYSTEM DEPENDENCIES + PYTHON PACKAGES (ROBUSTNESS FIRST)
# ===================================================================
RUN mkdir -p /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    chmod 644 /etc/apt/keyrings/winehq-archive.key && \
    apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    # CRITICAL: Install all ML/quant dependencies with exact pins that work on Python 3.10
    pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    # FIX: Make 'python' command available for supervisor & scripts (Render + KasmVNC)
    ln -sf /usr/bin/python3 /usr/bin/python || true && \
    # Clean up to keep image small
    rm -rf /var/lib/apt/lists/*

# ===================================================================
# SUPERVISOR CONFIG (MT5 + AI Bot run in parallel)
# ===================================================================
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Persistent volume for MT5 configuration, Wine data, and FBS login
VOLUME ["/config"]

# Ensure required runtime directories exist at build time (helpers.py also creates them)
RUN mkdir -p /app/data/historical /app/models /app/logs && \
    chmod -R 777 /app

# Start supervisor (runs both MT5 server + ai-trading-bot)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]