FROM gmag11/metatrader5_vnc:latest

# Copy your entire trading system
COPY . /app
WORKDIR /app

RUN mkdir -p /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    chmod 644 /etc/apt/keyrings/winehq-archive.key && \
    # Now safe to update and install
    apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    # Install Python dependencies (mt5linux + your stack)
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Supervisor config to run MT5 server + your bot in parallel
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Persistent volume for MT5 configuration and FBS login
VOLUME ["/config"]

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]