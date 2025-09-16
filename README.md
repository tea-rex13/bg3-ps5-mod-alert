# BG3 PS5 Mod Alert

Small Python tool that emails me whenever a **new PS5-approved mod** for **Baldur’s Gate 3** appears on [mod.io](https://mod.io/).  
It stores the last known PS5 mod count locally and alerts only when the number increases.

---

## Features (current)

- ✅ **PS5-only** counting via `X-Modio-Platform: ps5`
- ✅ CLI with `--baseline`, `--interval-mins`, `--test-email`, `--find-game`
- ✅ Local state (`state.json`) to avoid duplicate emails
- ✅ macOS **LaunchAgent** to run on a schedule (07:00, 14:00, 19:00)
- ✅ Reliability: **retry/backoff**, **spike guard** (`MAX_DELTA`), and **--dry-run**

---

## Quick Start

```bash
# 1) clone & enter the repo
git clone <your repo url> bg3-ps5-mod-alert
cd bg3-ps5-mod-alert

# 2) create & activate venv
python3 -m venv .venv
source .venv/bin/activate

# 3) install deps
python -m pip install -r requirements.txt

# 4) set up env (copy and edit)
cp .env.example .env
# Fill in MODIO_API_KEY and Gmail SMTP details, see below.

# 5) (optional) discover the BG3 slug/id
python -m src.mod_alert --find-game baldur
# Expect: "6715  Baldur's Gate 3   (slug: baldursgate3)"

# 6) set a baseline so first run doesn’t email
python -m src.mod_alert --baseline 800   # use the real current PS5 value

# 7) run once
python -m src.mod_alert


## HOW TO RUN

# run once (updates state.json; emails only if count increased)
python -m src.mod_alert

# safe test (no state changes, no email)
python -m src.mod_alert --dry-run

# send a test email
python -m src.mod_alert --test-email

# loop forever every 30 minutes
python -m src.mod_alert --interval-mins 30

# helper: search games (shows id + slug)
python -m src.mod_alert --find-game baldur


## ***CONFIGURATION (.env)***

# mod.io
MODIO_API_KEY=your_modio_api_key_here
MODIO_GAME_ID=baldursgate3     # slug or numeric id (slug recommended)
MODIO_PLATFORM=ps5             # do not change unless needed
# Optional host override (we try both automatically)
# MODIO_BASE=https://g-1.modapi.io/v1

# Email (Gmail App Password recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your_app_password
ALERT_TO=you@gmail.com

# Reliability (optional – defaults shown)
HTTP_TIMEOUT=15
HTTP_TRIES=3
HTTP_BACKOFF=2.0
MAX_DELTA=200   # ignore absurd jumps larger than this

## ***Scheduling on macOS (Step 07)

# Runs at 07:00, 14:00, 19:00 every day using a LaunchAgent.

# One-time install (recommended)

# from repo root
./scripts/install-launchagent.sh

# run once now (sanity)
launchctl start com.bg3.modalert

# check logs
tail -n 50 ~/Library/Logs/bg3_modalert.out.log
tail -n 50 ~/Library/Logs/bg3_modalert.err.log

The installer writes ~/Library/LaunchAgents/com.bg3.modalert.plist from the template in docs/com.bg3.modalert.plist and loads it.

Updating schedule: edit the template → rerun the installer:

launchctl unload ~/Library/LaunchAgents/com.bg3.modalert.plist
./scripts/install-launchagent.sh
launchctl load  ~/Library/LaunchAgents/com.bg3.modalert.plist

How it Works

Loads .env.

Resolves MODIO_GAME_ID (slug → numeric id).

Calls /games/{id}/mods with X-Modio-Platform: ps5 and reads result_total.

Compares to state.json’s last_count.

If increased: sends an email and updates last_count.

Reliability & Safety (Step 08)

Retries/backoff for transient HTTP errors (429/5xx) and network blips.

Spike guard: if current - last_count > MAX_DELTA, treat it as a glitch → no email, no baseline update.

--dry-run: print the count and exit (no state/email).

--verbose: show retry/backoff logs.

Examples:

python -m src.mod_alert --dry-run
python -m src.mod_alert --verbose
MAX_DELTA=1 python -m src.mod_alert   # test the spike guard

Repo Structure
bg3-ps5-mod-alert/
├─ src/
│  ├─ __init__.py
│  ├─ mod_alert.py      # main CLI / watcher
│  ├─ state.py          # JSON state load/save
│  └─ mailer.py         # SMTP email sender
├─ docs/
│  └─ com.bg3.modalert.plist  # LaunchAgent template (versioned)
├─ scripts/
│  └─ install-launchagent.sh  # installs/loads the LaunchAgent
├─ .env.example
├─ .gitignore
├─ requirements.txt
└─ README.md


state.json is created at runtime and ignored by git.

Troubleshooting

No email?

Use --test-email.

Ensure SMTP_USER uses a Gmail App Password (not your normal password).

Count looks too big (thousands)?

Ensure MODIO_PLATFORM=ps5 and you’re not using an unfiltered endpoint.

ModuleNotFoundError: No module named 'src'

Always run with python -m src.mod_alert from the repo root.

LaunchAgent didn’t run?

Check logs in ~/Library/Logs/.

Mac asleep at run time → run was skipped.

.env not loading?

Keep .env at repo root; we load it via dotenv at startup.



```
