# 🛡️ MikroTik Fail2Ban

[English](#english) | [Русский](#russian)

---

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com)
[![RouterOS](https://img.shields.io/badge/RouterOS-v6%2Fv7-green.svg)](https://mikrotik.com)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Made with ❤️](https://img.shields.io/badge/made%20with-%E2%9D%A4%EF%B8%8F-red.svg)](https://run-as-daemon.ru)

**Production-ready** | **RouterOS v6/v7** | **Docker & Bare Metal** | **Security-first**

</div>

---

## <a name="english"></a> 🇬🇧 English Version

### 📋 Quick Navigation

- [🚀 Quick Start](#quick-start-en)
  - [🐳 Docker Deployment](#docker-deployment-en)
  - [🖥️ Bare Metal Setup](#bare-metal-setup-en)
- [⚙️ MikroTik RouterOS Configuration](#routeros-configuration-en)
- [📁 Configuration Files](#configuration-files-en)
- [🧪 Testing](#testing-en)
- [🔒 Security Considerations](#security-en)
- [🛠️ Troubleshooting](#troubleshooting-en)
- [💼 Professional Services](#professional-services-en)
- [👨‍💻 Author & Support](#author-support-en)

---

### 🎯 About

Enhanced **Fail2Ban** integration for **MikroTik RouterOS** with comprehensive Docker support and production-ready deployment templates.

This is an enhanced fork of [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban) maintained by [@ranas-mukminov](https://github.com/ranas-mukminov), providing production-ready Fail2Ban templates, Docker containers, and automated testing for protecting MikroTik routers from brute-force attacks.

---

### ✨ Features

- 🔒 **Fail2Ban Filters** - Detection for MikroTik login failures (SSH, Winbox, L2TP, SSTP, OpenVPN)
- 🐳 **Docker Support** - Ready-to-use Docker Compose configuration
- ✅ **Automated Tests** - Pytest-based filter validation and CI/CD
- 🔄 **Address-List Sync** - Ban IPs on both Linux firewall and MikroTik router
- 📝 **RouterOS v6 & v7** - Compatible examples and scripts for both versions
- 🛡️ **Security-First** - Conservative defaults and best practices
- 🌐 **Remote Syslog** - Centralized log collection from MikroTik devices
- 🚀 **Production-Ready** - Tested in real-world environments

---

### 🏗️ Architecture

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

---

### <a name="quick-start-en"></a> 🚀 Quick Start

#### <a name="docker-deployment-en"></a> 🐳 Docker Deployment (Recommended)

Get started in 3 commands:

```bash
# 1. Clone the repository
git clone https://github.com/ranas-mukminov/mikrotik-fail2ban.git && cd mikrotik-fail2ban

# 2. Prepare configuration directories
mkdir -p docker/data/{filter.d,jail.d,action.d} && cp fail2ban/jail.d/*.conf docker/data/jail.d/

# 3. Start Fail2Ban container
cd docker && docker-compose up -d
```

**Verify installation:**

```bash
docker-compose exec fail2ban fail2ban-client status
docker-compose logs -f
```

#### <a name="bare-metal-setup-en"></a> 🖥️ Bare Metal Linux Setup

**Quick installation:**

```bash
# 1. Install Fail2Ban (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y fail2ban

# 2. Copy filters and jails
sudo cp fail2ban/filter.d/*.conf /etc/fail2ban/filter.d/
sudo cp fail2ban/jail.d/*.conf /etc/fail2ban/jail.d/

# 3. Enable jails and restart
sudo nano /etc/fail2ban/jail.d/mikrotik-login.conf  # Set enabled = true
sudo systemctl restart fail2ban
```

---

### <a name="routeros-configuration-en"></a> ⚙️ MikroTik RouterOS Configuration

#### Step 1: Configure Remote Logging

Send MikroTik logs to your Linux Fail2Ban server:

```routeros
# Replace YOUR_LINUX_IP with your server's IP address
/system logging action add name=remote target=remote remote=YOUR_LINUX_IP remote-port=514

# Add logging rules for different services
/system logging add topics=system,info,error action=remote
/system logging add topics=l2tp,info action=remote
/system logging add topics=sstp,info action=remote
/system logging add topics=ovpn,info,error action=remote
```

#### Step 2: Create Firewall Address Lists Rules

Block IPs from Fail2Ban address lists:

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

⚠️ **Important:** Place these rules early in your firewall filter chain, before any accept rules for these services.

<details>
<summary><b>Step 3: Optional - RouterOS Local Scripts</b></summary>

The repository includes RouterOS scripts that can run directly on the router to ban IPs locally:

- **`l2tpfail2ban/`** - Script for L2TP/SSTP failures
- **`login-fail2ban/`** - Script for generic login failures  
- **`openvpn-fail2ban/`** - Script for OpenVPN failures

These scripts complement the Linux-based Fail2Ban but are not required if you're using the remote syslog approach.

</details>

---

### <a name="configuration-files-en"></a> 📁 Configuration Files

#### Fail2Ban Filters

Located in `fail2ban/filter.d/`:

| Filter | Purpose | Log Patterns |
|--------|---------|--------------|
| **mikrotik-login.conf** | SSH, Winbox, API login failures | `login failure for user` |
| **mikrotik-l2tp.conf** | L2TP and SSTP authentication failures | `sent CHAP Failure` |
| **mikrotik-ovpn.conf** | OpenVPN authentication failures | `authentication failed` |

#### Fail2Ban Jails

Located in `fail2ban/jail.d/`:

| Jail | Filter | Address List | Default Settings |
|------|--------|--------------|------------------|
| **mikrotik-login** | mikrotik-login | badip | maxretry=3, findtime=600s, bantime=3600s |
| **mikrotik-l2tp** | mikrotik-l2tp | badl2tp | maxretry=3, findtime=600s, bantime=3600s |
| **mikrotik-ovpn** | mikrotik-ovpn | badovpn | maxretry=3, findtime=600s, bantime=3600s |

**Jail Configuration Parameters:**

- `maxretry = 3` - Ban after 3 failed attempts
- `findtime = 600` - Within 10 minutes window
- `bantime = 3600` - Ban duration 1 hour

💡 Adjust these values in jail configuration files based on your security requirements.

---

### <a name="testing-en"></a> 🧪 Testing

#### Filter Tests

Run automated tests to verify filter regex patterns:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Test specific filter
pytest tests/test_filters.py::test_mikrotik_login_filter -v
```

**Tests verify:**
- ✅ Failed login attempts are correctly matched
- ✅ Successful logins are NOT matched
- ✅ All filter regex patterns are valid

#### Docker Image Testing

Test the Docker image before deployment:

```bash
# Build and test
docker build -f docker/Dockerfile -t mikrotik-fail2ban:test .
docker run -d --name test-f2b mikrotik-fail2ban:test

# Verify functionality
docker exec test-f2b fail2ban-client ping
# Expected: Server replied: pong

docker exec test-f2b fail2ban-client status

# Clean up
docker rm -f test-f2b
```

---

### <a name="security-en"></a> 🔒 Security Considerations

⚠️ **Important Security Notes:**

| ⚠️ Warning | Description |
|------------|-------------|
| **Second Line of Defense** | Fail2Ban is NOT a replacement for strong passwords, key-based authentication, IP allowlists, VPN, or regular security updates |
| **Never Expose Management** | Don't expose SSH, Winbox, or management ports directly to internet without VPN or strict IP filtering |
| **Monitor Logs** | Regularly review Fail2Ban logs, set up alerts for unusual activity, maintain ban lists |
| **Test First** | Always verify on non-production system, ensure alternative access methods, whitelist your own IP |
| **Whitelist Legitimate IPs** | Add trusted IPs to Fail2Ban ignoreip to prevent accidental lockouts |

**Best Practices:**

```bash
# Whitelist your management IPs in jail.local or jail.d/*.conf
ignoreip = 127.0.0.1/8 ::1 YOUR_ADMIN_IP/32
```

---

### <a name="troubleshooting-en"></a> 🛠️ Troubleshooting

<details>
<summary><b>Common Issues and Solutions</b></summary>

#### Issue: No logs received from MikroTik

**Check:**
```bash
# On Linux server - check if syslog is receiving logs
sudo tcpdump -i any -n port 514

# On MikroTik - verify logging action
/system logging action print
/system logging print where action=remote
```

**Solution:**
- Verify firewall allows UDP 514
- Check IP address configuration
- Ensure logging topics are configured

#### Issue: Fail2Ban not banning IPs

**Check:**
```bash
# Test filter manually
fail2ban-regex /var/log/syslog /etc/fail2ban/filter.d/mikrotik-login.conf

# Check jail status
fail2ban-client status mikrotik-login

# View Fail2Ban logs
tail -f /var/log/fail2ban.log
```

**Solution:**
- Verify jail is enabled (`enabled = true`)
- Check log file path matches actual syslog location
- Verify filter regex matches your log format

#### Issue: Docker container not starting

**Check:**
```bash
# View container logs
docker logs fail2ban

# Check container status
docker ps -a | grep fail2ban
```

**Solution:**
- Ensure proper volume mounts
- Verify jail configurations syntax
- Check for port conflicts (if exposing ports)

#### Issue: Accidental self-ban

**Solution:**
```bash
# Unban IP immediately
fail2ban-client set mikrotik-login unbanip YOUR_IP

# Or via Docker
docker-compose exec fail2ban fail2ban-client set mikrotik-login unbanip YOUR_IP

# Add to whitelist permanently in jail.d/*.conf:
ignoreip = YOUR_IP/32
```

</details>

<details>
<summary><b>Debugging Commands</b></summary>

```bash
# Check Fail2Ban version
fail2ban-client version

# List all jails
fail2ban-client status

# Detailed jail status
fail2ban-client status mikrotik-login

# Reload Fail2Ban configuration
fail2ban-client reload

# Test filter with sample log
fail2ban-regex "login failure for user admin from 192.168.1.100 via ssh" \
    /etc/fail2ban/filter.d/mikrotik-login.conf

# View banned IPs
fail2ban-client get mikrotik-login banip

# Manually ban/unban IP
fail2ban-client set mikrotik-login banip 192.168.1.100
fail2ban-client set mikrotik-login unbanip 192.168.1.100
```

</details>

---

### 💼 <a name="professional-services-en"></a> Professional DevOps Services

Need help with production deployment, custom integration, or enterprise support?

<div align="center">

### 🚀 [Professional DevOps Support](https://run-as-daemon.ru)

**We offer:**

- ✅ **Custom Fail2Ban Integration** - Tailored solutions for your infrastructure
- ✅ **MikroTik Security Hardening** - Complete security audit and implementation
- ✅ **Docker & Kubernetes Deployment** - Production-ready containerized solutions
- ✅ **Monitoring & Alerting Setup** - 24/7 monitoring with Prometheus, Grafana, alerts
- ✅ **Enterprise Support** - SLA-backed support and maintenance
- ✅ **Training & Consulting** - Team training on security best practices

📧 **Contact:** [run-as-daemon.ru](https://run-as-daemon.ru)  
💼 **Author:** [@ranas-mukminov](https://github.com/ranas-mukminov)

</div>

---

### <a name="author-support-en"></a> 👨‍💻 Author & Support

**Maintainer:** [@ranas-mukminov](https://github.com/ranas-mukminov)

#### Community Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/ranas-mukminov/mikrotik-fail2ban/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/ranas-mukminov/mikrotik-fail2ban/discussions)
- 📖 **Documentation:** [Wiki](https://github.com/ranas-mukminov/mikrotik-fail2ban/wiki)

#### Professional Support

For enterprise deployments, custom integrations, or priority support:

- 🌐 **Website:** [run-as-daemon.ru](https://run-as-daemon.ru)
- 📧 **Email:** Available on website
- 💼 **Services:** DevOps consulting, infrastructure automation, security hardening

---

### 📜 License & Credits

**License:** This project maintains the same license as the original repository.

**Credits:**
- **Original Project:** [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban)
- **Enhanced Fork:** [@ranas-mukminov](https://github.com/ranas-mukminov)
- **Inspired by:** Various Fail2Ban and Docker integration projects

---

### 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Keep changes focused and add tests
4. Ensure all tests pass (`pytest tests/`)
5. Update documentation as needed
6. Submit a Pull Request

**Development Guidelines:**
- Follow existing code style
- Add tests for new filters or patterns
- Update README for significant changes
- Keep commits focused and descriptive

---

### 📊 Compatibility

| Component | Version | Status |
|-----------|---------|--------|
| **RouterOS** | v6.x | ✅ Tested |
| **RouterOS** | v7.x | ✅ Tested |
| **Fail2Ban** | 0.11+ | ✅ Recommended |
| **Docker** | 20.10+ | ✅ Supported |
| **Docker Compose** | v2.x | ✅ Supported |

---

### 📚 Documentation Links

- 📖 [Fail2Ban Official Documentation](https://fail2ban.readthedocs.io/)
- 📖 [MikroTik Wiki - System Logging](https://wiki.mikrotik.com/wiki/Manual:System/Log)
- 📖 [MikroTik Security Hardening](https://help.mikrotik.com/docs/display/ROS/Securing+your+router)
- 🐳 [Docker Documentation](https://docs.docker.com/)

---

<div align="center">

Made with ❤️ by [@ranas-mukminov](https://github.com/ranas-mukminov)

**Professional DevOps Support:** [run-as-daemon.ru](https://run-as-daemon.ru)

⭐ Star this repository if you find it useful!

</div>

---
---

## <a name="russian"></a> 🇷🇺 Русская версия

### 📋 Быстрая навигация

- [🚀 Быстрый старт](#quick-start-ru)
  - [🐳 Развертывание Docker](#docker-deployment-ru)
  - [🖥️ Установка на Linux](#bare-metal-setup-ru)
- [⚙️ Настройка MikroTik RouterOS](#routeros-configuration-ru)
- [📁 Файлы конфигурации](#configuration-files-ru)
- [🧪 Тестирование](#testing-ru)
- [🔒 Вопросы безопасности](#security-ru)
- [🛠️ Решение проблем](#troubleshooting-ru)
- [💼 Профессиональные услуги](#professional-services-ru)
- [👨‍💻 Автор и поддержка](#author-support-ru)

---

### 🎯 О проекте

Расширенная интеграция **Fail2Ban** для **MikroTik RouterOS** с полной поддержкой Docker и готовыми шаблонами для production.

Это улучшенный форк проекта [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban), поддерживаемый [@ranas-mukminov](https://github.com/ranas-mukminov). Проект предоставляет готовые к использованию шаблоны Fail2Ban, Docker-контейнеры и автоматизированное тестирование для защиты роутеров MikroTik от брутфорс-атак.

---

### ✨ Возможности

- 🔒 **Фильтры Fail2Ban** - Обнаружение неудачных попыток входа в MikroTik (SSH, Winbox, L2TP, SSTP, OpenVPN)
- 🐳 **Поддержка Docker** - Готовая конфигурация Docker Compose
- ✅ **Автоматизированное тестирование** - Проверка фильтров с помощью pytest и CI/CD
- 🔄 **Синхронизация address-list** - Блокировка IP на Linux firewall и MikroTik роутере
- 📝 **RouterOS v6 и v7** - Совместимые примеры и скрипты для обеих версий
- 🛡️ **Безопасность прежде всего** - Консервативные настройки по умолчанию и лучшие практики
- 🌐 **Удаленный Syslog** - Централизованный сбор логов с устройств MikroTik
- 🚀 **Готовность к production** - Протестировано в реальных условиях

---

### 🏗️ Архитектура

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  MikroTik       │         │  Linux Сервер    │         │  MikroTik       │
│  RouterOS       │ ──────> │  + Fail2Ban      │ ──────> │  Address Lists  │
│                 │  syslog │                  │   SSH/  │                 │
│  • L2TP         │         │  • Парсинг логов │   API   │  • badip        │
│  • OpenVPN      │         │  • Поиск атак    │         │  • badl2tp      │
│  • SSH/Winbox   │         │  • Блокировка IP │         │  • badovpn      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**Как это работает:**

1. **MikroTik** отправляет логи на удаленный Linux-сервер через syslog (UDP порт 514)
2. **Fail2Ban** на Linux парсит логи, используя пользовательские фильтры для обнаружения неудачных попыток аутентификации
3. **Fail2Ban** блокирует вредоносные IP локально, используя iptables
4. **Опционально:** Fail2Ban синхронизирует блокировки обратно в address-lists MikroTik через SSH или API для блокировки на уровне роутера

---

### <a name="quick-start-ru"></a> 🚀 Быстрый старт

#### <a name="docker-deployment-ru"></a> 🐳 Развертывание Docker (рекомендуется)

Начните работу за 3 команды:

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ranas-mukminov/mikrotik-fail2ban.git && cd mikrotik-fail2ban

# 2. Подготовьте директории конфигурации
mkdir -p docker/data/{filter.d,jail.d,action.d} && cp fail2ban/jail.d/*.conf docker/data/jail.d/

# 3. Запустите контейнер Fail2Ban
cd docker && docker-compose up -d
```

**Проверка установки:**

```bash
docker-compose exec fail2ban fail2ban-client status
docker-compose logs -f
```

#### <a name="bare-metal-setup-ru"></a> 🖥️ Установка на Linux

**Быстрая установка:**

```bash
# 1. Установите Fail2Ban (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y fail2ban

# 2. Скопируйте фильтры и jail-конфигурации
sudo cp fail2ban/filter.d/*.conf /etc/fail2ban/filter.d/
sudo cp fail2ban/jail.d/*.conf /etc/fail2ban/jail.d/

# 3. Включите jail и перезапустите
sudo nano /etc/fail2ban/jail.d/mikrotik-login.conf  # Установите enabled = true
sudo systemctl restart fail2ban
```

---

### <a name="routeros-configuration-ru"></a> ⚙️ Настройка MikroTik RouterOS

#### Шаг 1: Настройка удаленного логирования

Отправьте логи MikroTik на ваш Linux-сервер с Fail2Ban:

```routeros
# Замените YOUR_LINUX_IP на IP-адрес вашего сервера
/system logging action add name=remote target=remote remote=YOUR_LINUX_IP remote-port=514

# Добавьте правила логирования для различных сервисов
/system logging add topics=system,info,error action=remote
/system logging add topics=l2tp,info action=remote
/system logging add topics=sstp,info action=remote
/system logging add topics=ovpn,info,error action=remote
```

#### Шаг 2: Создание правил firewall для address-lists

Блокируйте IP из address-lists Fail2Ban:

```routeros
# Блокировка попыток входа (SSH, Winbox, API)
/ip firewall filter add chain=input src-address-list=badip action=drop \
    comment="fail2ban: блокировка плохих IP от SSH/Winbox/API"

# Блокировка попыток L2TP/SSTP
/ip firewall filter add chain=input protocol=tcp dst-port=1701 \
    src-address-list=badl2tp action=drop \
    comment="fail2ban: блокировка плохих L2TP IP"
/ip firewall filter add chain=input protocol=tcp dst-port=443 \
    src-address-list=badl2tp action=drop \
    comment="fail2ban: блокировка плохих SSTP IP"

# Блокировка попыток OpenVPN
/ip firewall filter add chain=input protocol=tcp dst-port=1194 \
    src-address-list=badovpn action=drop \
    comment="fail2ban: блокировка плохих OpenVPN IP"
/ip firewall filter add chain=input protocol=udp dst-port=1194 \
    src-address-list=badovpn action=drop \
    comment="fail2ban: блокировка плохих OpenVPN IP"
```

⚠️ **Важно:** Размещайте эти правила в начале цепочки firewall filter, перед любыми правилами accept для этих сервисов.

<details>
<summary><b>Шаг 3: Опционально - Локальные скрипты RouterOS</b></summary>

Репозиторий включает скрипты RouterOS, которые могут работать непосредственно на роутере для локальной блокировки IP:

- **`l2tpfail2ban/`** - Скрипт для ошибок L2TP/SSTP
- **`login-fail2ban/`** - Скрипт для общих ошибок входа
- **`openvpn-fail2ban/`** - Скрипт для ошибок OpenVPN

Эти скрипты дополняют Linux-based Fail2Ban, но не требуются, если вы используете подход с удаленным syslog.

</details>

---

### <a name="configuration-files-ru"></a> 📁 Файлы конфигурации

#### Фильтры Fail2Ban

Расположены в `fail2ban/filter.d/`:

| Фильтр | Назначение | Паттерны логов |
|--------|------------|----------------|
| **mikrotik-login.conf** | Неудачные попытки SSH, Winbox, API | `login failure for user` |
| **mikrotik-l2tp.conf** | Ошибки аутентификации L2TP и SSTP | `sent CHAP Failure` |
| **mikrotik-ovpn.conf** | Ошибки аутентификации OpenVPN | `authentication failed` |

#### Jail-конфигурации Fail2Ban

Расположены в `fail2ban/jail.d/`:

| Jail | Фильтр | Address List | Настройки по умолчанию |
|------|--------|--------------|------------------------|
| **mikrotik-login** | mikrotik-login | badip | maxretry=3, findtime=600s, bantime=3600s |
| **mikrotik-l2tp** | mikrotik-l2tp | badl2tp | maxretry=3, findtime=600s, bantime=3600s |
| **mikrotik-ovpn** | mikrotik-ovpn | badovpn | maxretry=3, findtime=600s, bantime=3600s |

**Параметры конфигурации Jail:**

- `maxretry = 3` - Блокировка после 3 неудачных попыток
- `findtime = 600` - В течение окна 10 минут
- `bantime = 3600` - Длительность блокировки 1 час

💡 Настройте эти значения в файлах конфигурации jail в соответствии с вашими требованиями безопасности.

---

### <a name="testing-ru"></a> 🧪 Тестирование

#### Тестирование фильтров

Запустите автоматизированные тесты для проверки regex-паттернов фильтров:

```bash
# Установите зависимости для тестов
pip install -r tests/requirements.txt

# Запустите все тесты
pytest tests/ -v

# Тестирование конкретного фильтра
pytest tests/test_filters.py::test_mikrotik_login_filter -v
```

**Тесты проверяют:**
- ✅ Неудачные попытки входа правильно обнаруживаются
- ✅ Успешные входы НЕ обнаруживаются
- ✅ Все regex-паттерны фильтров корректны

#### Тестирование Docker-образа

Протестируйте Docker-образ перед развертыванием:

```bash
# Сборка и тестирование
docker build -f docker/Dockerfile -t mikrotik-fail2ban:test .
docker run -d --name test-f2b mikrotik-fail2ban:test

# Проверка функциональности
docker exec test-f2b fail2ban-client ping
# Ожидается: Server replied: pong

docker exec test-f2b fail2ban-client status

# Очистка
docker rm -f test-f2b
```

---

### <a name="security-ru"></a> 🔒 Вопросы безопасности

⚠️ **Важные замечания по безопасности:**

| ⚠️ Предупреждение | Описание |
|-------------------|----------|
| **Вторая линия защиты** | Fail2Ban НЕ заменяет сильные пароли, аутентификацию по ключам, белые списки IP, VPN или регулярные обновления безопасности |
| **Не открывайте управление** | Не открывайте SSH, Winbox или порты управления напрямую в интернет без VPN или строгой фильтрации IP |
| **Мониторинг логов** | Регулярно просматривайте логи Fail2Ban, настройте оповещения о необычной активности, поддерживайте списки блокировок |
| **Сначала тестируйте** | Всегда проверяйте на не-production системе, обеспечьте альтернативные методы доступа, добавьте ваш IP в белый список |
| **Белый список легитимных IP** | Добавьте доверенные IP в ignoreip Fail2Ban, чтобы предотвратить случайную блокировку |

**Лучшие практики:**

```bash
# Добавьте ваши управленческие IP в белый список в jail.local или jail.d/*.conf
ignoreip = 127.0.0.1/8 ::1 YOUR_ADMIN_IP/32
```

---

### <a name="troubleshooting-ru"></a> 🛠️ Решение проблем

<details>
<summary><b>Распространенные проблемы и решения</b></summary>

#### Проблема: Не получаются логи от MikroTik

**Проверка:**
```bash
# На Linux-сервере - проверьте, получает ли syslog логи
sudo tcpdump -i any -n port 514

# На MikroTik - проверьте действие логирования
/system logging action print
/system logging print where action=remote
```

**Решение:**
- Проверьте, что firewall разрешает UDP 514
- Проверьте конфигурацию IP-адреса
- Убедитесь, что темы логирования настроены

#### Проблема: Fail2Ban не блокирует IP

**Проверка:**
```bash
# Протестируйте фильтр вручную
fail2ban-regex /var/log/syslog /etc/fail2ban/filter.d/mikrotik-login.conf

# Проверьте статус jail
fail2ban-client status mikrotik-login

# Просмотрите логи Fail2Ban
tail -f /var/log/fail2ban.log
```

**Решение:**
- Проверьте, что jail включен (`enabled = true`)
- Проверьте, что путь к файлу логов совпадает с реальным расположением syslog
- Проверьте, что regex фильтра соответствует вашему формату логов

#### Проблема: Docker-контейнер не запускается

**Проверка:**
```bash
# Просмотр логов контейнера
docker logs fail2ban

# Проверка статуса контейнера
docker ps -a | grep fail2ban
```

**Решение:**
- Убедитесь в правильном монтировании томов
- Проверьте синтаксис конфигураций jail
- Проверьте наличие конфликтов портов (если порты открыты)

#### Проблема: Случайная само-блокировка

**Решение:**
```bash
# Немедленно разблокируйте IP
fail2ban-client set mikrotik-login unbanip YOUR_IP

# Или через Docker
docker-compose exec fail2ban fail2ban-client set mikrotik-login unbanip YOUR_IP

# Добавьте в белый список навсегда в jail.d/*.conf:
ignoreip = YOUR_IP/32
```

</details>

<details>
<summary><b>Команды отладки</b></summary>

```bash
# Проверка версии Fail2Ban
fail2ban-client version

# Список всех jail
fail2ban-client status

# Детальный статус jail
fail2ban-client status mikrotik-login

# Перезагрузка конфигурации Fail2Ban
fail2ban-client reload

# Тест фильтра с примером лога
fail2ban-regex "login failure for user admin from 192.168.1.100 via ssh" \
    /etc/fail2ban/filter.d/mikrotik-login.conf

# Просмотр заблокированных IP
fail2ban-client get mikrotik-login banip

# Ручная блокировка/разблокировка IP
fail2ban-client set mikrotik-login banip 192.168.1.100
fail2ban-client set mikrotik-login unbanip 192.168.1.100
```

</details>

---

### 💼 <a name="professional-services-ru"></a> Профессиональные DevOps услуги

Нужна помощь с production развертыванием, кастомной интеграцией или корпоративной поддержкой?

<div align="center">

### 🚀 [Профессиональная DevOps поддержка](https://run-as-daemon.ru)

**Мы предлагаем:**

- ✅ **Кастомная интеграция Fail2Ban** - Решения, адаптированные под вашу инфраструктуру
- ✅ **Усиление безопасности MikroTik** - Полный аудит безопасности и внедрение
- ✅ **Развертывание Docker и Kubernetes** - Production-ready контейнеризированные решения
- ✅ **Настройка мониторинга и оповещений** - 24/7 мониторинг с Prometheus, Grafana, alerting
- ✅ **Корпоративная поддержка** - Поддержка и обслуживание с SLA
- ✅ **Обучение и консалтинг** - Обучение команды лучшим практикам безопасности

📧 **Контакты:** [run-as-daemon.ru](https://run-as-daemon.ru)  
💼 **Автор:** [@ranas-mukminov](https://github.com/ranas-mukminov)

</div>

---

### <a name="author-support-ru"></a> 👨‍💻 Автор и поддержка

**Поддержка проекта:** [@ranas-mukminov](https://github.com/ranas-mukminov)

#### Поддержка сообщества

- 🐛 **Проблемы:** [GitHub Issues](https://github.com/ranas-mukminov/mikrotik-fail2ban/issues)
- 💬 **Обсуждения:** [GitHub Discussions](https://github.com/ranas-mukminov/mikrotik-fail2ban/discussions)
- 📖 **Документация:** [Wiki](https://github.com/ranas-mukminov/mikrotik-fail2ban/wiki)

#### Профессиональная поддержка

Для корпоративных развертываний, кастомных интеграций или приоритетной поддержки:

- 🌐 **Сайт:** [run-as-daemon.ru](https://run-as-daemon.ru)
- 📧 **Email:** Доступен на сайте
- 💼 **Услуги:** DevOps консалтинг, автоматизация инфраструктуры, усиление безопасности

---

### 📜 Лицензия и благодарности

**Лицензия:** Этот проект использует ту же лицензию, что и оригинальный репозиторий.

**Благодарности:**
- **Оригинальный проект:** [soriel/mikrotik-fail2ban](https://github.com/soriel/mikrotik-fail2ban)
- **Улучшенный форк:** [@ranas-mukminov](https://github.com/ranas-mukminov)
- **Вдохновлен:** Различными проектами интеграции Fail2Ban и Docker

---

### 🤝 Участие в разработке

Вклад приветствуется! Пожалуйста:

1. Форкните репозиторий
2. Создайте feature-ветку (`git checkout -b feature/my-feature`)
3. Держите изменения фокусированными и добавляйте тесты
4. Убедитесь, что все тесты проходят (`pytest tests/`)
5. Обновите документацию при необходимости
6. Отправьте Pull Request

**Рекомендации по разработке:**
- Следуйте существующему стилю кода
- Добавляйте тесты для новых фильтров или паттернов
- Обновляйте README для значительных изменений
- Держите коммиты фокусированными и описательными

---

### �� Совместимость

| Компонент | Версия | Статус |
|-----------|--------|--------|
| **RouterOS** | v6.x | ✅ Протестировано |
| **RouterOS** | v7.x | ✅ Протестировано |
| **Fail2Ban** | 0.11+ | ✅ Рекомендуется |
| **Docker** | 20.10+ | ✅ Поддерживается |
| **Docker Compose** | v2.x | ✅ Поддерживается |

---

### 📚 Ссылки на документацию

- 📖 [Официальная документация Fail2Ban](https://fail2ban.readthedocs.io/)
- 📖 [MikroTik Wiki - Системное логирование](https://wiki.mikrotik.com/wiki/Manual:System/Log)
- �� [Усиление безопасности MikroTik](https://help.mikrotik.com/docs/display/ROS/Securing+your+router)
- 🐳 [Документация Docker](https://docs.docker.com/)

---

<div align="center">

Сделано с ❤️ [@ranas-mukminov](https://github.com/ranas-mukminov)

**Профессиональная DevOps поддержка:** [run-as-daemon.ru](https://run-as-daemon.ru)

⭐ Поставьте звезду этому репозиторию, если он вам полезен!

</div>

