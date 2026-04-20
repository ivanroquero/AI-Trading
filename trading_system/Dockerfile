FROM gmag11/metatrader5_vnc:latest

# Copy your entire trading system
COPY . /app
WORKDIR /app

# Install Python deps (mt5linux client + your stack)
RUN apt-get update && apt-get install -y supervisor && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Supervisor to run MT5 server + your bot in parallel
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Persistent MT5 config + login (FBS demo)
VOLUME ["/config"]

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]