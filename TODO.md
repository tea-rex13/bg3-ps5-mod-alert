# BG3 PS5 Mod Alert — Learning Project TODOs

This is my step-by-step plan to build a Python script that alerts me by email when a new BG3 mod appears on PS5.  
Each step is a separate branch + PR so the repo history tells the “story” of the build.

---

- [x] **Step 00 — Repo created**

  - Create repo on GitHub (`bg3-ps5-mod-alert`)
  - Clone locally
  - Make initial branch `step-00-repo-created` and push
  - (Optional) Add a README line to show there’s a difference
  - Open PR and merge into `main`

- [x] **Step 01 — Project skeleton**

  - Create new branch `step-01-skeleton`
  - Add `.venv/` Python virtual environment
  - Add `requirements.txt` with `requests` and `python-dotenv`
  - Create `src/` folder with `__init__.py`
  - Add `.gitignore` to exclude venv, `.env`, cache, state file
  - Update `README.md` with skeleton description
  - Commit + push + open PR + merge

- [x] **Step 02 — Config & secrets**

  - New branch `step-02-config`
  - Add `.env.example` for API key + email settings
  - Create local `.env` (not committed)
  - Update README with setup instructions
  - Commit + push + PR + merge

- [x] **Step 03 — function outline**

  - New branch `get-mod-count-api`
  - Add `get_mod_count()` stub that raises `NotImplementedError`
  - Commit + push + PR + merge

- [x] **Step 04 — Watcher scaffold**
  - `state.py` (JSON load/save)
  - `mailer.py` (SMTP via `.env`, tested; note macOS certs fix)
  - `mod_alert.py` (`run_check`, CLI: `--test-email`, `--baseline`, `--interval-mins`)
- [x] **Step 05 — Documentation polish**
  - Clean `.env.example` placeholders (no secrets)
  - README: setup, running, env variables, TLS fix note, troubleshooting
- [x] **Step 06 — Implement `get_mod_count` (mod.io API)**
  - `.env` keys: `MODIO_API_KEY`, `MODIO_GAME_ID`, `MODIO_PLATFORM=ps5`
  - Add `--find-game <name>` helper to discover game ID
  - Use `result_total` (fallback to `len(data)` if needed)
- [x] **Step 07 — Scheduling**
  - macOS LaunchAgent instructions (run every N minutes)
- [x] **Step 08 — Nice-to-haves**
  - Logging + retries
  - `--simulate` mode / cooldown batching
  - Unit tests for state/mailer/count
