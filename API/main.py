import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from API.harness.loop import run_turn
from shared.data import load_data, save_data


def run_scenario(scenario_path: str, out_path: str):
    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    save_data({"participants": {}})
    memory_state = {}
    per_session_results = []

    for session in scenario.get("sessions", []):
        session_out = {
            "session_id": session["session_id"],
            "user": session["user"],
            "turns": []
        }
        for turn in session.get("turns", []):
            result = run_turn(session["session_id"], session["user"], turn["input"], memory_state)
            session_out["turns"].append({
                "turn_id": turn["id"],
                "input": turn["input"],
                "response": result["response"],
                "usage": result["usage"],
                "stop_reason": result["stop_reason"],
            })
        per_session_results.append(session_out)

    payload = {
        "scenario": scenario_path,
        "results": per_session_results,
        "database_snapshot": load_data(),
    }

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the API diet-tracker scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_scenario(args.scenario, args.out)
    print(f"API scenario saved to {args.out}")
