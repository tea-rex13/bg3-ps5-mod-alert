import json, os, time
STATE_PATH = "state.json"

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f: return json.load(f)
    return {"last_count": None, "last_checked": None}

def save_state(state):
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=2)
