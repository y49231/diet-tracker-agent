import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SDK.agent import SDKDietAgent
from shared.data import load_data, save_data
from shared.agent_config import EFFORT, MODEL


async def _run_scenario(scenario_path: str, out_path: str, offline=False, data_path=None):
    import shared.data as data_store

    original_data_path = data_store.DATA_FILE
    output_path = Path(out_path)
    data_path = data_path or output_path.parent / f"{output_path.stem}_state" / "database.json"
    try:
        if data_path:
            data_store.DATA_FILE = str(data_path)
        with open(scenario_path, "r", encoding="utf-8") as f:
            scenario = json.load(f)
        save_data({"participants": {}})
        agent = SDKDietAgent(offline=offline)
        session_results = []
        for session in scenario.get("sessions", []):
            user = session["user"]
            turns = []
            for turn in session.get("turns", []):
                context = load_data().get("participants", {}).get(user, {})
                if offline:
                    outcome = agent.handle(session["session_id"], user, turn["input"])
                else:
                    outcome = await agent.handle_async(
                        session["session_id"], user, turn["input"], context=context
                    )
                turns.append({
                    "turn_id": turn["id"], "input": turn["input"],
                    "response": outcome["response"], "tool_used": outcome["tool_used"],
                    "tool_names": outcome.get("tool_names", [outcome.get("tool_name")] if outcome.get("tool_name") else []),
                    "usage": outcome.get("usage", {}),
                    "session_usage": outcome.get("session_usage", {}),
                    "total_cost_usd": outcome.get("usage", {}).get("total_cost_usd"),
                    "api_calls": outcome.get("api_calls", 0),
                    "duration_ms": outcome.get("duration_ms", 0),
                    "expected_tool": turn.get("expected_tools", [None])[0],
                })
            session_results.append({"session_id": session["session_id"], "user": user, "turns": turns})
            if not offline and session["session_id"] in agent.clients:
                await agent.clients[session["session_id"]].disconnect()

        payload = {
            "mode": "offline" if offline else "live",
            "model": None if offline else MODEL,
            "effort": None if offline else EFFORT,
            "results": session_results,
            "database_snapshot": load_data(),
        }
        out_file = output_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload
    finally:
        data_store.DATA_FILE = original_data_path


def run_scenario(scenario_path: str, out_path: str, offline=False, data_path=None):
    return asyncio.run(_run_scenario(scenario_path, out_path, offline, data_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SDK diet-tracker scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--data")
    args = parser.parse_args()
    run_scenario(args.scenario, args.out, args.offline, args.data)
    print(f"SDK scenario saved to {args.out}")
