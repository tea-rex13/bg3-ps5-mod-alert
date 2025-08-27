# src/mod_alert.py
import time
import argparse
from .state import load_state, save_state
from .mailer import send_email

# --- still a stub; implement in Step 04 ---
def get_mod_count() -> int:
    raise NotImplementedError("Implement get_mod_count() in Step 04.")

def run_check():
    state = load_state()
    current = get_mod_count()  # will raise until implemented
    last = state["last_count"]

    if last is None:
        state["last_count"] = current  # set baseline on first successful run
    elif current > last:
        diff = current - last
        send_email(
            f"[BG3] New PS5 mod(s): +{diff} (now {current})",
            f"The PS5 mod count increased from {last} to {current}."
        )
        state["last_count"] = current

    state["last_checked"] = int(time.time())
    save_state(state)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval-mins", type=int, default=0,
                        help="If >0, run forever every N minutes. If 0, run once.")
    parser.add_argument("--test-email", action="store_true",
                        help="Send a test email and exit.")
    parser.add_argument("--baseline", type=int,
                        help="Set/override baseline count and exit.")
    args = parser.parse_args()

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
    except NotImplementedError as e:
        print(str(e))

if __name__ == "__main__":
    main()

