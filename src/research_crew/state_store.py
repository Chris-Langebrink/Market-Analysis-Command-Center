import json, os
from pathlib import Path

STATE_PATH = Path(__file__).parent / "output" / "state.json"
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_topic(topic: str) -> dict | None:
    return load_state().get(topic)

def set_topic(topic: str, payload: dict) -> None:
    s = load_state()
    s[topic] = payload
    save_state(s)
