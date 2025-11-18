#!/bin/sh
set -e

echo "Starting mikrotik-fail2ban Docker container..."

# Copy custom configurations if provided
if [ -d /data/filter.d ] && [ "$(ls -A /data/filter.d 2>/dev/null)" ]; then
    echo "Copying custom filters from /data/filter.d..."
    cp -v /data/filter.d/*.conf /etc/fail2ban/filter.d/ 2>/dev/null || true
fi

if [ -d /data/jail.d ] && [ "$(ls -A /data/jail.d 2>/dev/null)" ]; then
    echo "Copying custom jails from /data/jail.d..."
    cp -v /data/jail.d/*.conf /etc/fail2ban/jail.d/ 2>/dev/null || true
fi

if [ -d /data/action.d ] && [ "$(ls -A /data/action.d 2>/dev/null)" ]; then
    echo "Copying custom actions from /data/action.d..."
    cp -v /data/action.d/*.conf /etc/fail2ban/action.d/ 2>/dev/null || true
fi

# Create necessary directories
mkdir -p /var/run/fail2ban /var/log

# Touch log files that might be needed by jails
touch /var/log/auth.log /var/log/syslog /var/log/messages

# Start rsyslog for log collection (suppress kernel log error)
echo "Starting rsyslog..."
rsyslogd -n >/dev/null 2>&1 &

# Give rsyslog a moment to start
sleep 1

echo "Starting fail2ban-server in foreground..."
# Start Fail2Ban in foreground with:
# -f: foreground mode
# -x: force execution (don't check for running instance)
# -v: verbose logging
exec fail2ban-server -f -x -v start
