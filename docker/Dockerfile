FROM debian:bookworm-slim

LABEL maintainer="ranas-mukminov"
LABEL description="Fail2Ban for MikroTik RouterOS log monitoring"

# Install Fail2Ban, Python, and required utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fail2ban \
        python3 \
        python3-pip \
        iptables \
        rsyslog \
        && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /data/filter.d /data/jail.d /data/action.d

# Copy Fail2Ban configuration templates
COPY fail2ban/filter.d/*.conf /etc/fail2ban/filter.d/
COPY fail2ban/jail.d/*.conf /etc/fail2ban/jail.d/

# Create a startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Copy custom configurations if provided\n\
if [ -d /data/filter.d ] && [ "$(ls -A /data/filter.d)" ]; then\n\
    echo "Copying custom filters from /data/filter.d..."\n\
    cp -v /data/filter.d/*.conf /etc/fail2ban/filter.d/ || true\n\
fi\n\
\n\
if [ -d /data/jail.d ] && [ "$(ls -A /data/jail.d)" ]; then\n\
    echo "Copying custom jails from /data/jail.d..."\n\
    cp -v /data/jail.d/*.conf /etc/fail2ban/jail.d/ || true\n\
fi\n\
\n\
if [ -d /data/action.d ] && [ "$(ls -A /data/action.d)" ]; then\n\
    echo "Copying custom actions from /data/action.d..."\n\
    cp -v /data/action.d/*.conf /etc/fail2ban/action.d/ || true\n\
fi\n\
\n\
# Start rsyslog for log collection\n\
rsyslogd\n\
\n\
# Start Fail2Ban in foreground\n\
exec fail2ban-server -f -x -v start\n\
' > /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose volume for custom configurations
VOLUME ["/data"]

# Expose syslog port for receiving MikroTik logs
EXPOSE 514/tcp 514/udp

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
