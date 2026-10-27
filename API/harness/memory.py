import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEMORY_PATH = ROOT / "results" / "api_memory.json"


def load_memory():
    print("[API.harness.memory] Loading memory state")
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_PATH.exists():
        return {}
    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_memory(data):
    print("[API.harness.memory] Saving memory state")
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_memory(user_name):
    memory = load_memory()
    return memory.get(user_name, {})


def remember_user(user_name, updates):
    memory = load_memory()
    user_data = memory.setdefault(user_name, {})
    user_data.update(updates)
    save_memory(memory)
    return user_data
