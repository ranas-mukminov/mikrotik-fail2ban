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

# Copy jail.local to disable default Debian jails
COPY docker/jail.local /etc/fail2ban/jail.local

# Copy and set up entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose volume for custom configurations
VOLUME ["/data"]

# Expose syslog port for receiving MikroTik logs
EXPOSE 514/tcp 514/udp

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
