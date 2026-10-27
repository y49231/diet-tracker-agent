import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SDK.agent import SDKDietAgent
from shared.data import load_data, save_data


def run_scenario(scenario_path: str, out_path: str):
    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    save_data({"participants": {}})
    agent = SDKDietAgent()
    session_results = []

    for session in scenario.get("sessions", []):
        user = session["user"]
        turns = []
        for turn in session.get("turns", []):
            outcome = agent.handle(session["session_id"], user, turn["input"])
            turns.append({
                "turn_id": turn["id"],
                "input": turn["input"],
                "response": outcome["response"],
                "tool_used": outcome["tool_used"],
            })
        session_results.append({
            "session_id": session["session_id"],
            "user": user,
            "turns": turns,
        })

    payload = {
        "scenario": scenario_path,
        "results": session_results,
        "database_snapshot": load_data(),
    }

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SDK diet-tracker scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_scenario(args.scenario, args.out)
    print(f"SDK scenario saved to {args.out}")
