# mikrotik-fail2ban

Enhanced Fail2Ban integration for MikroTik RouterOS with Docker support.

This is an enhanced fork of [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban) maintained by [@ranas-mukminov](https://github.com/ranas-mukminov), providing production-ready Fail2Ban templates, Docker containers, and automated testing for protecting MikroTik routers from brute-force attacks.

## Features

- 🔒 **Fail2Ban filters** for MikroTik login failures (SSH, Winbox, L2TP, SSTP, OpenVPN)
- 🐳 **Docker-ready setup** with docker-compose for easy deployment
- ✅ **Automated tests** with pytest to ensure filter accuracy
- 🔄 **Address-list sync** to ban IPs on both Linux firewall and MikroTik router
- 📝 **RouterOS v6 & v7 compatible** examples and scripts
- 🛡️ **Conservative defaults** for security-first approach

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  MikroTik       │         │  Linux Server    │         │  MikroTik       │
│  RouterOS       │ ──────> │  + Fail2Ban      │ ──────> │  Address Lists  │
│                 │  syslog │                  │   SSH/  │                 │
│  • L2TP         │         │  • Parse logs    │   API   │  • badip        │
│  • OpenVPN      │         │  • Detect fails  │         │  • badl2tp      │
│  • SSH/Winbox   │         │  • Ban IPs       │         │  • badovpn      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**How it works:**

1. **MikroTik** sends logs to a remote Linux server via syslog (UDP port 514)
2. **Fail2Ban** on Linux parses logs using custom filters to detect failed authentication attempts
3. **Fail2Ban** bans malicious IPs locally using iptables
4. **Optional:** Fail2Ban syncs bans back to MikroTik address-lists via SSH or API for router-level blocking

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository:**

```bash
git clone https://github.com/ranas-mukminov/mikrotik-fail2ban.git
cd mikrotik-fail2ban
```

2. **Create custom configuration directories:**

```bash
mkdir -p docker/data/{filter.d,jail.d,action.d}
```

3. **Copy and customize jail configurations:**

```bash
# Copy example jails
cp fail2ban/jail.d/*.conf docker/data/jail.d/

# Edit jails to enable them and set your preferences
nano docker/data/jail.d/mikrotik-login.conf
# Change: enabled = false  ->  enabled = true
```

4. **Start the container:**

```bash
cd docker
docker-compose up -d
```

5. **Check status:**

```bash
docker-compose exec fail2ban fail2ban-client status
docker-compose logs -f
```

### Option 2: Bare Metal Linux

1. **Install Fail2Ban:**

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install fail2ban

# RedHat/CentOS
sudo yum install fail2ban
```

2. **Copy filter and jail configurations:**

```bash
# Copy filters
sudo cp fail2ban/filter.d/*.conf /etc/fail2ban/filter.d/

# Copy jails
sudo cp fail2ban/jail.d/*.conf /etc/fail2ban/jail.d/
```

3. **Enable and customize jails:**

```bash
# Edit jail files and set enabled = true
sudo nano /etc/fail2ban/jail.d/mikrotik-login.conf
```

4. **Restart Fail2Ban:**

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

## MikroTik RouterOS Configuration

### Step 1: Configure Log Actions

Configure MikroTik to send logs to your Linux server running Fail2Ban:

```routeros
# Replace YOUR_LINUX_IP with your server's IP address
/system logging action add name=remote target=remote remote=YOUR_LINUX_IP remote-port=514

# Add logging rules for different services
/system logging add topics=system,info,error action=remote
/system logging add topics=l2tp,info action=remote
/system logging add topics=sstp,info action=remote
/system logging add topics=ovpn,info,error action=remote
```

### Step 2: Configure Firewall Address Lists

Create firewall rules to block IPs from Fail2Ban address lists:

```routeros
# Block generic login attempts (SSH, Winbox, API)
/ip firewall filter add chain=input src-address-list=badip action=drop \
    comment="fail2ban: block bad IPs from SSH/Winbox/API"

# Block L2TP/SSTP attempts
/ip firewall filter add chain=input protocol=tcp dst-port=1701 \
    src-address-list=badl2tp action=drop \
    comment="fail2ban: block bad L2TP IPs"
/ip firewall filter add chain=input protocol=tcp dst-port=443 \
    src-address-list=badl2tp action=drop \
    comment="fail2ban: block bad SSTP IPs"

# Block OpenVPN attempts
/ip firewall filter add chain=input protocol=tcp dst-port=1194 \
    src-address-list=badovpn action=drop \
    comment="fail2ban: block bad OpenVPN IPs"
/ip firewall filter add chain=input protocol=udp dst-port=1194 \
    src-address-list=badovpn action=drop \
    comment="fail2ban: block bad OpenVPN IPs"
```

**Important:** Place these rules early in your firewall filter chain, before any accept rules for these services.

### Step 3: Optional - RouterOS Scripts for Local Banning

The repository includes RouterOS scripts that can run directly on the router to ban IPs locally:

- `l2tpfail2ban/` - Script for L2TP/SSTP failures
- `login-fail2ban/` - Script for generic login failures
- `openvpn-fail2ban/` - Script for OpenVPN failures

These scripts complement the Linux-based Fail2Ban but are not required if you're using the remote syslog approach.

## Configuration Files

### Fail2Ban Filters

Located in `fail2ban/filter.d/`:

- **mikrotik-login.conf** - Detects failed SSH, Winbox, API login attempts
- **mikrotik-l2tp.conf** - Detects failed L2TP and SSTP authentication (CHAP failures)
- **mikrotik-ovpn.conf** - Detects failed OpenVPN authentication

### Fail2Ban Jails

Located in `fail2ban/jail.d/`:

- **mikrotik-login.conf** - Jail for generic login failures
- **mikrotik-l2tp.conf** - Jail for L2TP/SSTP failures
- **mikrotik-ovpn.conf** - Jail for OpenVPN failures

**Default settings:**
- `maxretry = 3` - Ban after 3 failed attempts
- `findtime = 600` - Within 10 minutes
- `bantime = 3600` - Ban duration 1 hour

Adjust these values in the jail configuration files based on your security requirements.

## Testing

Run the automated tests to verify filter regex patterns:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run tests
pytest tests/ -v
```

Tests verify that:
- Failed login attempts are correctly matched
- Successful logins are NOT matched
- All filter regex patterns are valid

## Docker Details

### Building the Image

```bash
docker build -f docker/Dockerfile -t mikrotik-fail2ban:latest .
```

### Testing the Image

After building, you can test the image to ensure fail2ban-server is running properly:

```bash
# Start the container
docker run -d --name test-container mikrotik-fail2ban:latest

# Wait a few seconds for startup
sleep 5

# Test that fail2ban is running
docker exec test-container fail2ban-client ping
# Expected output: Server replied: pong

# Check the version
docker exec test-container fail2ban-client version

# Check status
docker exec test-container fail2ban-client status

# View logs
docker logs test-container

# Clean up
docker rm -f test-container
```

### Environment Variables

- `TZ` - Timezone (default: UTC)

### Volumes

- `/data/filter.d` - Custom filter configurations
- `/data/jail.d` - Custom jail configurations
- `/data/action.d` - Custom action configurations
- `/var/log` - Host log files (for log parsing)
- `/var/lib/fail2ban` - Fail2Ban database (persists bans across restarts)

### Network Modes

The docker-compose example uses `network_mode: host` for simplicity. This allows Fail2Ban to apply iptables rules directly to the host's INPUT chain.

**Alternative:** Use bridge network and configure Fail2Ban to use the DOCKER-USER chain for better isolation.

## Security Considerations

⚠️ **Important Security Notes:**

1. **Fail2Ban is a second line of defense**, not a replacement for:
   - Strong passwords or key-based authentication
   - IP allowlists for administrative access
   - VPN for remote management
   - Regular security updates

2. **Never expose management ports to the internet** without proper protection:
   - Use VPN for remote access
   - Implement IP-based access control
   - Change default ports where possible

3. **Monitor your logs:**
   - Regularly review Fail2Ban logs
   - Set up alerts for unusual activity
   - Maintain ban lists and whitelist legitimate IPs

4. **Test before deploying:**
   - Verify on a non-production system first
   - Ensure you have alternative access methods
   - Whitelist your own IP to avoid lockouts

## Address List Names

This fork maintains compatibility with original address-list names:

- `badip` - Generic failed login attempts (SSH, Winbox, API, etc.)
- `badl2tp` - Failed L2TP and SSTP attempts
- `badovpn` - Failed OpenVPN attempts

These names are used in:
- RouterOS firewall rules
- RouterOS scripts in `l2tpfail2ban/`, `login-fail2ban/`, `openvpn-fail2ban/`
- Custom Fail2Ban actions (when syncing bans back to MikroTik)

## Contributing

Contributions are welcome! Please:

1. Work on feature branches (e.g., `feature/my-feature`)
2. Keep changes focused and small
3. Add tests for new filters or patterns
4. Update documentation as needed
5. Ensure all tests pass before submitting PR

## Compatibility

- **RouterOS:** Compatible with RouterOS v6 and v7
- **Fail2Ban:** Tested with Fail2Ban 0.11+
- **Docker:** Compatible with Docker Engine 20.10+ and Docker Compose v2

## License

This project maintains the same license as the original [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban) repository.

## Credits

- Original project: [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban)
- Enhanced fork maintained by: [@ranas-mukminov](https://github.com/ranas-mukminov)
- Inspired by various Fail2Ban and Docker integration projects

## Support

For issues, questions, or contributions:
- Open an issue: https://github.com/ranas-mukminov/mikrotik-fail2ban/issues
- Submit a PR: https://github.com/ranas-mukminov/mikrotik-fail2ban/pulls

---

**Remember:** Always test in a safe environment before deploying to production! 🛡️
