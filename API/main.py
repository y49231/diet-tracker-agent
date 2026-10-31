import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from API.harness.loop import run_turn
from API.harness import history as history_store
from API.harness import memory as memory_store
from API.agent import MessagesAPIAgent
from shared.data import load_data, save_data
from shared.agent_config import EFFORT, MODEL


def run_scenario(scenario_path: str, out_path: str, offline=False, data_path=None, history_dir=None, memory_path=None):
    import shared.data as data_store

    output_path = Path(out_path)
    state_dir = output_path.parent / f"{output_path.stem}_state"
    data_path = data_path or state_dir / "database.json"
    history_dir = history_dir or state_dir / "history"
    memory_path = memory_path or state_dir / "memory.json"
    originals = (data_store.DATA_FILE, history_store.HISTORY_DIR, memory_store.MEMORY_PATH)
    try:
        if data_path:
            data_store.DATA_FILE = str(data_path)
        if history_dir:
            history_store.HISTORY_DIR = Path(history_dir)
        if memory_path:
            memory_store.MEMORY_PATH = Path(memory_path)
        with open(scenario_path, "r", encoding="utf-8") as f:
            scenario = json.load(f)
        save_data({"participants": {}})
        memory_state = {}
        agent = None if offline else MessagesAPIAgent()
        per_session_results = []
        for session in scenario.get("sessions", []):
            session_out = {"session_id": session["session_id"], "user": session["user"], "turns": []}
            for turn in session.get("turns", []):
                result = run_turn(
                    session["session_id"], session["user"], turn["input"], memory_state, agent=agent
                )
                session_out["turns"].append({
                    "turn_id": turn["id"], "input": turn["input"],
                    "response": result["response"], "tool_names": result["tool_names"],
                    "tool_calls": result["tool_calls"],
                    "usage": result["usage"], "api_calls": result["api_calls"],
                    "duration_ms": result["duration_ms"], "model": result["model"],
                    "effort": result["effort"], "stop_reason": result["stop_reason"],
                    "expected_tool": turn.get("expected_tools", [None])[0],
                })
            per_session_results.append(session_out)
        payload = {
            "mode": "offline" if offline else "live",
            "model": None if offline else MODEL,
            "effort": None if offline else EFFORT,
            "results": per_session_results,
            "database_snapshot": load_data(),
        }
        out_file = output_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload
    finally:
        data_store.DATA_FILE, history_store.HISTORY_DIR, memory_store.MEMORY_PATH = originals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the API diet-tracker scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--data")
    parser.add_argument("--history-dir")
    parser.add_argument("--memory")
    args = parser.parse_args()
    run_scenario(args.scenario, args.out, args.offline, args.data, args.history_dir, args.memory)
    print(f"API scenario saved to {args.out}")
