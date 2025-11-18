#!/bin/sh
set -e

echo "=== MikroTik Fail2Ban Container Starting ==="

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

# Create dummy log files for fail2ban jails that might reference them
# This prevents errors even if jails are disabled
touch /var/log/auth.log /var/log/syslog /var/log/messages

# Start rsyslog for log collection (suppress kernel log warnings)
echo "Starting rsyslog..."
rsyslogd 2>/dev/null || true

echo "Starting fail2ban-server in foreground..."
echo "Fail2Ban will monitor MikroTik logs configured in /etc/fail2ban/jail.d/"
echo ""

# Start Fail2Ban in foreground mode
# -f: foreground
# -x: force execution of the server (skip PID check)
# -v: verbose
exec fail2ban-server -f -x -v start
