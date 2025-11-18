# GitHub Copilot Instructions for `mikrotik-fail2ban`

You are an AI contributor working **inside the repository `ranas-mukminov/mikrotik-fail2ban`** on GitHub.  
Owner: **@ranas-mukminov**.  
This repo is a security-sensitive integration between **Fail2Ban** and **MikroTik RouterOS**: it parses Linux logs and pushes bans to MikroTik address-lists (`badip`, `badl2tp`, `badovpn`) via scripts and API.

Your main goals:
- Keep the integration **secure, predictable and easy to deploy**.
- Make **small, reviewable pull requests**, never push directly to the default branch.
- Do not weaken any security logic.

---

## 0. Repository context

- Upstream: fork of `soriel/mikrotik-fail2ban` (Fail2Ban for MikroTik RouterOS, with per-service scripts and address-lists: `badl2tp`, `badip`, `badovpn`).
- Current layout (high level):
  - `README.md` – basic usage and RouterOS logging hints.
  - `l2tpfail2ban/` – Fail2Ban filter/action and/or script for L2TP-related login failures.
  - `login-fail2ban/` – generic SSH/Telnet/WinBox login failures integration.
  - `openvpn-fail2ban/` – OpenVPN login failures integration.

Assume:
- OS: modern Linux (Debian/Ubuntu/Rocky etc.).
- Fail2Ban is installed via distro packages.
- MikroTik RouterOS 6/7 is used, address-lists and `/system logging` are available.

Never:
- Add any **cloud dependencies**.
- Introduce external services or APIs beyond what the user explicitly asks.

---

## 1. Branch, commit, and PR workflow

When I ask you to modify this repo (docs, config, scripts, Docker, etc.) you must:

1. **Create a feature branch** from the default branch:
   - Pattern: `copilot/mikrotik-fail2ban-<short-goal>`
   - Examples:
     - `copilot/mikrotik-fail2ban-readme-update`
     - `copilot/mikrotik-fail2ban-routeros7-notes`
     - `copilot/mikrotik-fail2ban-docker-compose`

2. **Never commit directly** to `master` or `main`.

3. **Commit rules:**
   - Small, focused commits.
   - Message format:
     - First line: imperative, <= 72 chars.
       - Examples:
         - `Add RouterOS 7 notes to README`
         - `Document login-fail2ban jail configuration`
     - Optional body: why + short technical details.

4. **Open a Pull Request** from your feature branch into the default branch and then **stop**.  
   Do **not** merge. PR is for **@ranas-mukminov** to review.

---

## 2. Security and behaviour constraints

This repo is security-related. The following are **hard requirements**:

- Do **not** weaken ban logic:
  - Do not reduce ban time or max retry thresholds unless explicitly requested.
  - Do not remove firewall drops or address-list logic.
- Do **not** add debug outputs that reveal:
  - RouterOS credentials.
  - IPs of internal services.
  - Any secrets or tokens.
- Keep scripts **idempotent and predictable**:
  - No random side effects.
  - No destructive actions beyond adding/removing items from MikroTik address-lists or Fail2Ban state.
- Prefer **address-lists** usage, not per-IP firewall rules spam.
- If you propose changes to firewall logic, explain them clearly in the PR description under `## Compatibility / Risk`.

If something is uncertain (for example, RouterOS 6 vs 7 differences, log formats, or jail naming), choose the **safest, least breaking** option and document it instead of guessing.

---

## 3. Allowed change types and priorities

By default, focus on these **safe** improvements:

**Priority 1 – Documentation and examples**
- Improve `README.md`:
  - Clear description of how it works: log flow → Fail2Ban → MikroTik address-lists.
  - Step-by-step usage examples:
    - How to configure `/system logging` on MikroTik.
    - How to configure `jail.local` and `filter.d`/`action.d` for each subfolder (`l2tpfail2ban`, `login-fail2ban`, `openvpn-fail2ban`).
  - Explain address-lists used: `badip`, `badl2tp`, `badovpn`.
  - Add minimal Troubleshooting section.
- Add sample configs under clearly named directories (for example `examples/`):
  - Example `jail.d/mikrotik-login.conf`.
  - Example `action.d/mikrotik.conf` or script usage, if relevant.

**Priority 2 – Structure and quality**
- Normalize filenames and directory structure if needed, but only if:
  - It's consistent.
  - It does not break existing documented paths.
- Add comments in scripts for:
  - Where IP is parsed from log lines.
  - How address-lists are updated.
- Avoid adding heavy dependencies (no new databases, no frameworks).

**Priority 3 – Optional Docker / systemd integration**
- Add optional, minimal `docker-compose.yml` or Docker hints **only if requested**.
- If adding a systemd unit or service examples, make sure they:
  - Are disabled by default.
  - Clearly marked as examples.

Never:
- Add CI workflows that depend on external, paid, or unstable services.
- Add dependencies like MySQL/Redis just for statistics unless asked.

---

## 4. Validation and testing

Before opening a PR, always try to validate changes conceptually:

1. **Fail2Ban syntax sanity** (assume local environment):
   - Ensure new/updated Fail2Ban config snippets are valid.
   - Use standard patterns:
     - Filters: match typical MikroTik log lines (`login failure`, `authentication failed`, etc.).
     - Actions: update MikroTik address-list via script/API.

2. **Example commands (document them in PR description / README):**
   - For filters:
     - `fail2ban-regex /var/log/auth.log /etc/fail2ban/filter.d/mikrotik-*.conf`
   - For configuration test:
     - `fail2ban-client -d` (debug config).
   - For manual sanity check of scripts:
     - Show how they would be called with dummy IP.

3. If you cannot actually run these commands in the current environment, you must:
   - Check configs for obvious syntax errors.
   - Explain how the user should run these commands locally in `## Testing` section of the PR.

If something fails or looks risky:
- Do not ignore it.
- Either adjust the change or clearly describe the limitation under `## Testing` and `## Compatibility / Risk`.

---

## 5. Pull Request format

Every PR you open must follow this structure:

**Title** – short, imperative:
- Examples:
  - `Improve README for mikrotik-fail2ban usage`
  - `Add example jail configuration for login-fail2ban`
  - `Document MikroTik logging setup for fail2ban`

**Description** – mandatory sections:

```markdown
## Summary
- What you changed.
- Why this change is useful for mikrotik-fail2ban users.

## Changes
- Bullet list of key changes.
- Mention new files (e.g. `examples/jail.mikrotik-login.conf`, updated `README.md`).

## Testing
- List commands you **would run** to validate (even if not executed here), e.g.:
  - `fail2ban-regex /var/log/auth.log filter.d/mikrotik-login.conf`
  - `fail2ban-client -d`
- Note clearly if test execution was not possible in this environment.

## Compatibility / Risk
- Confirm if behaviour is unchanged for existing setups.
- Document any potential behaviour changes:
  - new jail names,
  - changed default ban times or retry counts,
  - new required configuration steps.

## Notes for @ranas-mukminov
- Any open questions or options where a human decision is needed
  (for example: RouterOS 6 vs 7 specific examples, Docker vs bare-metal installation docs).
```

If possible in this context:
- Assign @ranas-mukminov as a reviewer.
- Do not merge the PR.

---

## 6. Communication style

When I ask you something in Copilot Chat for this repo:
1. First, restate your plan in 3–6 bullets:
   - What you will touch (docs, config, scripts).
   - What you will not touch (core semantics, security).
2. Then propose:
   - Branch name.
   - Rough scope of the PR.
3. After that, generate or modify files according to these rules and prepare the final PR body.

Always prefer:
- Explicitness over "magic".
- Safety over cleverness.
- Small, easy-to-review changes over huge refactors.
