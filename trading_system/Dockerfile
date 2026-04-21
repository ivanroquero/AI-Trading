FROM gmag11/metatrader5_vnc:latest

# Copy your entire trading system
COPY . /app
WORKDIR /app

# Wine key (kept exactly as you had it — harmless and already present)
RUN mkdir -p /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    chmod 644 /etc/apt/keyrings/winehq-archive.key && \
    apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    # CRITICAL FIX: --break-system-packages is the correct, safe pattern in controlled Docker trading containers
    pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Supervisor config to run MT5 server + AI bot in parallel
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Persistent volume for MT5 configuration and FBS login
VOLUME ["/config"]

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]