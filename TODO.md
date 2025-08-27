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

- [x] **Step 03 — funct outline**

  - New branch get-mod-count-api``
  - Write Python funct script to:
    - raise implement error as func isnt written yet

- [ ] **Step 04 — Watcher script**

  - New branch `step-04-watcher-script`
  - Write Python script to:
    - Find BG3 game id via mod.io API
    - Fetch PS5 mod count
    - Store last count in JSON
    - Send email when count increases
  - Test with `--simulate`
  - Commit + push + PR + merge

- [ ] **Step 05 — Documentation polish**

  - New branch `step-04-qol`
  - Expand README with “How it works” and “Running locally”
  - Add instructions for installing deps, running script
  - Commit + push + PR + merge

- [ ] **Step 06 — Scheduling**

  - New branch `step-05-cron`
  - Add notes (`docs/cron.md`) on running with `cron` (Mac)
  - Commit + push + PR + merge

- [ ] **Step 07 — GitHub Actions (optional but nice)**
  - New branch `step-06-actions`
  - Add `.github/workflows/schedule.yml` to run hourly
  - Store secrets in GitHub Actions
  - Commit + push + PR + merge

---

### Notes

- Keep each step small: branch → commit(s) → PR → merge.
- Update this file as you go — tick `[x]` when done.
