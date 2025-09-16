# BG3 PS5 Mod Alert

A tiny Python tool that emails you whenever a **new PS5-approved mod** for **Baldur’s Gate 3** appears on [mod.io](https://mod.io/).

It tracks the last known PS5 mod count locally and alerts only when the number increases.  
Built to be simple, reliable, and easy to run from Terminal or on a schedule (macOS LaunchAgent).

---

## ✨ Features

- **PS5-only** counting via `X-Modio-Platform: ps5` (no all-platform overcounts)
- CLI: `--baseline`, `--interval-mins`, `--test-email`, `--find-game`, `--dry-run`, `--verbose`
- Local state (`state.json`) to prevent duplicate emails
- macOS **LaunchAgent** schedule (07:00, 14:00, 19:00 daily)
- Reliability: HTTP **retries/backoff** + **spike guard** (`MAX_DELTA`)
- One-command runner (`run.sh`) and versioned LaunchAgent template + installer

---

## 🗂️ Repo Structure

bg3-ps5-mod-alert/
├─ src/
│ ├─ init.py
│ ├─ mod_alert.py # main CLI / watcher (PS5-only, retries, dry-run, spike guard)
│ ├─ state.py # JSON state load/save helpers
│ └─ mailer.py # SMTP email sender
├─ docs/
│ └─ com.bg3.modalert.plist # LaunchAgent template (versioned; uses placeholders)
├─ scripts/
│ └─ install-launchagent.sh # installs/loads LaunchAgent with real paths
├─ run.sh # convenience wrapper for python -m src.mod_alert
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md # this file

> `state.json` is created at runtime and **ignored by git**.

---

## 🚀 Quick Start

```bash
# 1) clone & enter
git clone <REPO_URL> bg3-ps5-mod-alert
cd bg3-ps5-mod-alert

# 2) venv + deps
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# 3) configure env
cp .env.example .env
# Fill in MODIO_API_KEY and Gmail SMTP settings (see below)

# 4) find the BG3 slug/id (helper)
python -m src.mod_alert --find-game baldur
# Expect: "6715  Baldur's Gate 3   (slug: baldursgate3)"
# In .env, set: MODIO_GAME_ID=baldursgate3

# 5) set a baseline so the first run doesn’t email
python -m src.mod_alert --baseline 800   # use the actual current PS5 value

# 6) run once
python -m src.mod_alert

#Configuration (.env)

#Copy .env.example → .env then fill (secrets stay local; .env is ignored by git):

# mod.io
MODIO_API_KEY=your_modio_api_key_here
MODIO_GAME_ID=baldursgate3    # slug or numeric id (slug recommended)
MODIO_PLATFORM=ps5
# Optional host override (we try both automatically)
# MODIO_BASE=https://g-1.modapi.io/v1

# Email (use a Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your_app_password
ALERT_TO=you@gmail.com

# Reliability (optional – defaults shown)
HTTP_TIMEOUT=15
HTTP_TRIES=3
HTTP_BACKOFF=2.0
MAX_DELTA=200     # ignore absurd jumps larger than this in one run

##HOW TO RUN
# run once (updates state; emails only on increase)
python -m src.mod_alert

# safe dry-run (no email, no state writes)
python -m src.mod_alert --dry-run

# send a test email (SMTP sanity)
python -m src.mod_alert --test-email

# loop forever every 30 minutes
python -m src.mod_alert --interval-mins 30

# helper: search games (shows id + slug)
python -m src.mod_alert --find-game baldur


##SCHEDULING on mac
OS (07:00, 14:00, 19:00)

# from repo root
./scripts/install-launchagent.sh

# run once now (sanity)
launchctl start com.bg3.modalert

# logs
tail -n 50 ~/Library/Logs/bg3_modalert.out.log
tail -n 50 ~/Library/Logs/bg3_modalert.err.log


##RELIABILITY AND SAFETY

# Strict PS5 filter only (/games/{id}/mods + X-Modio-Platform: ps5)

# Retries/backoff for 429/5xx/network hiccups (configurable via .env)

# Spike guard: if current - last > MAX_DELTA, treat as glitch → no email, no baseline update

# --dry-run prints the current count and exits safely

# --verbose prints retry/backoff logs

#Examples:

python -m src.mod_alert --dry-run
python -m src.mod_alert --verbose
MAX_DELTA=1 python -m src.mod_alert   # force the spike guard to trigger

##TROUBLESHOOTING

# ModuleNotFoundError: No module named 'src'
# Always run with python -m src.mod_alert from the repo root (or use run.sh).

# No email sent
# Use --test-email. Ensure you’re using a Gmail App Password for SMTP_PASS.

# Count too large (thousands)
# Ensure MODIO_PLATFORM=ps5; we call the PS5-filtered endpoint only.

# LaunchAgent didn’t fire
# Check logs under ~/Library/Logs/. Note: if the Mac is asleep at the exact time, the run is skipped.

# .env not loading
# Keep .env in the repo root; we load it on module startup.

##LICENCE

#See Licence
```
