import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY_DIR = ROOT / "results" / "history"


def history_path(session_id):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_DIR / f"{session_id}.json"


def load_history(session_id):
    print(f"[API.harness.history] Loading session history: {session_id}")
    path = history_path(session_id)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def append_history(session_id, entry):
    print(f"[API.harness.history] Appending turn to session: {session_id}")
    history = load_history(session_id)
    history.append(entry)
    with history_path(session_id).open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return history
