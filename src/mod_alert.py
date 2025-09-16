# src/mod_alert.py
import time
import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from .state import load_state, save_state
from .mailer import send_email

_DRY_RUN = False
_VERBOSE = False


# Load .env from the repo root (one level up from /src)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ---- helpers ---------------------------------------------------------------

def find_games(query: str) -> None:
    """Search mod.io games and print ID + slug so you can set MODIO_GAME_ID."""
    base = os.getenv("MODIO_BASE") or "https://g-1.modapi.io/v1"
    key = os.getenv("MODIO_API_KEY")
    plat = (os.getenv("MODIO_PLATFORM") or "ps5").lower()
    if not key:
        raise RuntimeError("Set MODIO_API_KEY in your .env first.")
    r = _get(
        f"{base}/games",
        params={"api_key": key, "_q": query, "_limit": 50},
        headers={"X-Modio-Platform": plat},
        timeout=15,
    )
    r.raise_for_status()
    for g in r.json().get("data", []):
        print(f"{g['id']:>8}  {g.get('name')}   (slug: {g.get('name_id')})")

def _resolve_game_id(game_value: str) -> str:
    """Accepts a numeric ID or slug (e.g. 'baldursgate3'); returns numeric ID."""
    game_value = (game_value or "").strip()
    if game_value.isdigit():
        return game_value

    key = os.getenv("MODIO_API_KEY")
    plat = (os.getenv("MODIO_PLATFORM") or "ps5").lower()
    headers = {"X-Modio-Platform": plat, "Accept": "application/json"}
    params = {"api_key": key, "_limit": 1, "name_id": game_value}

    for base in [os.getenv("MODIO_BASE") or "https://g-1.modapi.io/v1", "https://api.mod.io/v1"]:
        try:
            r = _get(f"{base}/games", params=params, headers=headers, timeout=15)
            r.raise_for_status()
            items = r.json().get("data", [])
            if items:
                return str(items[0]["id"])
        except Exception:
            continue
    raise RuntimeError(f"Could not resolve game '{game_value}' on mod.io")

def get_mod_count() -> int:
    """
    Return the PS5-only mod count by calling /games/{id}/mods with X-Modio-Platform: ps5.
    No unfiltered fallbacks. If the filtered endpoint fails, raise RuntimeError.
    """
    key  = os.getenv("MODIO_API_KEY")
    game = (os.getenv("MODIO_GAME_ID") or "").strip()
    plat = (os.getenv("MODIO_PLATFORM") or "ps5").lower()
    if not key or not game:
        raise RuntimeError("Missing MODIO_API_KEY or MODIO_GAME_ID in .env")

    gid = _resolve_game_id(game)
    headers = {"X-Modio-Platform": plat, "Accept": "application/json"}
    params  = {"api_key": key, "_limit": 1}

    last_err = None
    for base in [os.getenv("MODIO_BASE") or "https://g-1.modapi.io/v1", "https://api.mod.io/v1"]:
        try:
            r = _get(f"{base}/games/{gid}/mods", params=params, headers=headers, timeout=15)
            if r.status_code == 404:
                last_err = f"404 at {r.url}"
                continue
            r.raise_for_status()
            data = r.json()
            total = data.get("result_total") or data.get("result_count") or len(data.get("data", []))
            return int(total)
        except Exception as e:
            last_err = str(e)
            continue

    raise RuntimeError(f"Could not fetch PS5-only mod count (last error: {last_err})")
def _sleep(sec: float):
    try:
        time.sleep(sec)
    except KeyboardInterrupt:
        raise

def _get(url, *, params=None, headers=None, timeout=None, tries=None, backoff=None):
    """requests.get with retries/backoff for 429/5xx and network errors."""
    timeout = timeout or int(os.getenv("HTTP_TIMEOUT", "15"))
    tries   = tries   or int(os.getenv("HTTP_TRIES", "3"))
    backoff = float(backoff or os.getenv("HTTP_BACKOFF", "2.0"))

    last_err = None
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                # use Retry-After if provided; otherwise exponential backoff
                ra = r.headers.get("Retry-After")
                delay = float(ra) if ra and ra.isdigit() else (backoff ** (attempt - 1))
                if _VERBOSE:
                    print(f"[retry] HTTP {r.status_code} -> sleeping {delay:.1f}s ({r.url})")
                _sleep(delay)
                last_err = RuntimeError(f"HTTP {r.status_code} @ {r.url}")
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last_err = e
            if attempt < tries:
                delay = backoff ** (attempt - 1)
                if _VERBOSE:
                    print(f"[retry] {e} -> sleeping {delay:.1f}s ({url})")
                _sleep(delay)
                continue
            break
    raise RuntimeError(f"request failed after {tries} tries: {last_err}")


# ---- watcher ---------------------------------------------------------------

def run_check():
    state = load_state()
    try:
        current = get_mod_count()
    except RuntimeError as e:
        print(f"Error fetching PS5 count: {e}")
        return  # do not change baseline / do not email

    # --- DRY RUN: no state updates, no email ---
    if _DRY_RUN:
        print(f"[dry-run] PS5 count = {current} (baseline={state.get('last_count')})")
        return

    last = state.get("last_count")

    # --- SPIKE GUARD ---
    # If the increase is absurdly large (API glitch), ignore it.
    max_delta = int(os.getenv("MAX_DELTA", "200"))  # tune via .env if you like
    if last is not None:
        delta = current - last
        if delta > max_delta:
            print(f"Ignoring spike {last} -> {current} (> MAX_DELTA={max_delta}).")
            # still record when we checked
            state["last_checked"] = int(time.time())
            save_state(state)
            return

    # --- Normal flow ---
    if last is None:
        state["last_count"] = current
    elif current > last:
        diff = current - last
        send_email(
            f"[BG3] New PS5 mod(s): +{diff} (now {current})",
            f"The PS5 mod count increased from {last} to {current}."
        )
        state["last_count"] = current

    state["last_checked"] = int(time.time())
    save_state(state)
    print("PS5 count =", current)


# ---- CLI -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval-mins", type=int, default=0,
                        help="If >0, run forever every N minutes. If 0, run once.")
    parser.add_argument("--test-email", action="store_true",
                        help="Send a test email and exit.")
    parser.add_argument("--baseline", type=int,
                        help="Set/override baseline count and exit.")
    parser.add_argument("--find-game", type=str,
                        help="Search mod.io games by name and print IDs.")
    # NEW flags
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and print; do not update state or send email.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose retry/backoff logging.")

    args = parser.parse_args()

    # Make flags visible to run_check()/network helpers
    global _DRY_RUN, _VERBOSE
    _DRY_RUN = args.dry_run
    _VERBOSE = args.verbose

    if args.find_game:
        find_games(args.find_game)
        return

    if args.test_email:
        send_email("BG3 Mod Alert – test", "If you see this, email is configured.")
        print("Test email sent.")
        return

    if args.baseline is not None:
        state = load_state()
        state["last_count"] = args.baseline
        state["last_checked"] = int(time.time())
        save_state(state)
        print(f"Baseline set to {args.baseline}.")
        return

    try:
        if args.interval_mins > 0:
            while True:
                run_check()
                time.sleep(args.interval_mins * 60)
        else:
            run_check()
    except RuntimeError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
