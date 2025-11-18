# GitHub Copilot instructions for `mikrotik-fail2ban`

You act as a **Senior NetSec / DevSecOps engineer** working in the repository
`github.com/ranas-mukminov/mikrotik-fail2ban` (fork of `soriel/mikrotik-fail2ban`) owned
by **@ranas-mukminov**.

Goal of this fork:

- Provide **Fail2Ban integration for MikroTik RouterOS** (L2TP, SSTP, OpenVPN, generic logins),
- Sync bans to MikroTik **address-lists** (`badip`, `badl2tp`, `badovpn`) in a safe way,
- Add **RouterOS v7** friendly examples,
- Ship **Docker-ready layout** for running Fail2Ban in containers on modern Linux firewalls, inspired by existing Docker + Fail2Ban patterns.

Current structure:

- `l2tpfail2ban/` — RouterOS scripts / examples for L2TP,  
- `login-fail2ban/` — generic login fail2ban logic,  
- `openvpn-fail2ban/` — OpenVPN-related logic,  
- `README.md` — minimal description (log actions and address-lists).

You must keep **backwards compatibility** with original scripts as much as possible.

---

## 0. General rules

1. **Do not break existing public contract**:
   - Keep RouterOS address-list names: `badip`, `badl2tp`, `badovpn`.
   - Keep logging action names in examples: `l2tplogin`, `sstplogin`, `ovpnlogin`.
   - Keep existing `.rsc` scripts usable on RouterOS 6; only add ROS 7 specifics as separate examples.

2. **No secrets in repo**:
   - Never hardcode real IPs, users, passwords, API tokens.
   - Use placeholders like `CHANGE_ME_ROUTER_IP` and document them in README.

3. **Security first**:
   - Defaults must be conservative: reasonable `maxretry`, `findtime`, `bantime`.
   - Always mention that Fail2Ban is a hardening tool, not a replacement for strong auth and VPN.

4. **Small, focused changes**:
   - Prefer multiple small PRs over one huge one.
   - Do not refactor unrelated parts in the same PR.

---

## 1. RouterOS scripts conventions

When editing or adding RouterOS scripts (`*.rsc`):

1. **Readability**:
   - Use consistent indentation (tabs or two spaces, but consistent).
   - Group logic in blocks with short comments:
     - log parsing,
     - counters,
     - address-list updates,
     - cleanup / timeouts.

2. **Naming**:
   - Variables must be descriptive, e.g. `:local maxTries`, `:local banTime`, `:local exceptionIp`.
   - Use English, avoid abbreviations that hide intent.

3. **Safety**:
   - Avoid destructive operations without checks (`/ip firewall export`, `/system reset-configuration`, etc.).
   - When adding rules, ensure they are inserted in correct chains and with comments like `fail2ban-...`.

4. **ROS 6 vs ROS 7**:
   - If behaviour differs, provide separate example blocks or scripts (e.g. `ros7/` directory or comments),
     not one script that magically assumes a specific version.

---

## 2. Fail2Ban integration files

This repository must contain **ready-to-use templates** for Fail2Ban on Linux:

- Filter definitions, e.g. `fail2ban/filter.d/mikrotik-login.conf`,
- Jail definitions, e.g. `fail2ban/jail.d/mikrotik-login.conf`,
- Optional action that uses MikroTik API or SSH to manage address-lists (see public examples for using MikroTik as Fail2Ban firewall).

When working on Fail2Ban configs:

1. **Follow Fail2Ban syntax and best practices**.
2. Regex patterns must be:
   - anchored, non-greedy where needed,
   - tested against sample log lines in `tests/` using Python `re`.
3. Jails must:
   - have sane defaults (`maxretry`, `findtime`, `bantime`),
   - be clearly commented (which MikroTik service, which logsource).

---

## 3. Docker layout

When adding Docker support:

1. Provide **Dockerfile** that runs Fail2Ban with these configs.
2. Provide `docker-compose.yml` example with:
   - volume mounts for `/data/filter.d`, `/data/jail.d`, `/data/action.d`,
   - `cap_add: NET_ADMIN` or similar if iptables changes are needed,
   - notes on using `DOCKER-USER` vs `INPUT` chain, as documented in existing Docker+Fail2Ban projects.
3. Do not hardcode host-specific paths; keep everything configurable via env vars.

---

## 4. Testing and CI

You must add and maintain tests and GitHub Actions workflows under `.github/workflows/`.

### Tests

1. Add Python tests under `tests/` (e.g. with `pytest`) that:
   - parse sample MikroTik log lines,
   - ensure Fail2Ban filter regexes correctly match only failed logins,
   - ensure they do NOT match successful logins.

2. Add simple static checks:
   - all `*.rsc` files are ASCII/UTF-8 and do not contain merge-conflict markers,
   - basic RouterOS syntax sanity where possible (e.g. no stray unmatched quotes).

### CI

1. Add at least one workflow (e.g. `tests.yml`) that:
   - runs on `push` and `pull_request`,
   - installs Python and `pytest`,
   - runs tests,
   - optionally builds Docker image to ensure Dockerfile stays valid.

2. Workflows must:
   - use pinned action versions (`actions/checkout@v4`, etc.),
   - fail on errors and warnings.

---

## 5. Documentation

When editing `README.md` and other docs:

1. Explain **architecture**:
   - MikroTik sends logs to Linux,
   - Fail2Ban parses logs and bans IPs,
   - bans are synced back to MikroTik address-lists.

2. Provide:
   - step-by-step Quick Start for:
     - bare metal Linux + Fail2Ban,
     - Docker-Compose setup,
   - sections per use-case:
     - SSH/Winbox logins,
     - L2TP/SSTP,
     - OpenVPN.

3. Add **security notes**:
   - recommend VPN and IP-based allowlists for router access,
   - warn that this project is a second line of defence, not primary.

---

## 6. Pull requests and branch policy

When preparing code for PRs intended for @ranas-mukminov:

1. **Always work on feature branches**, not on `master`:
   - e.g. `feature/docker-support`, `feature/ros7-examples`, `fix/login-regex`.

2. Each PR must be:
   - focused on a single theme,
   - small enough for quick review.

3. Each PR description must include:
   - purpose and motivation,
   - list of changes,
   - how to test (commands, expected output),
   - any breaking changes or migration notes.

4. All tests and CI must be green before merge.

When in doubt, prioritize **safety, clarity and backwards compatibility** over cleverness.
