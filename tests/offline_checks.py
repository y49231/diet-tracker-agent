import os
import sys
import json
import tempfile
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.data import load_data, save_data
from shared.tools import set_plan, log_food, check_recipe, log_weight, detect_food_name, classify_food
import shared.data as data_store
from API.harness import history as api_history
from API.harness import memory as api_memory
from API.harness.loop import run_turn
from SDK.agent import SDKDietAgent


def reset_db():
    base = {"participants": {}}
    save_data(base)


def test_plan_switch_ok():
    reset_db()
    result = set_plan("Dana", 1200)
    data = load_data()
    ok = "Dana" in data["participants"] and data["participants"]["Dana"]["plan"] == 1200 and "עודכנה" in result
    print(f"PASS test_plan_switch_ok: {ok}")
    return ok


def test_invalid_plan_rejected():
    reset_db()
    result = set_plan("Dana", 1300)
    ok = "שגיאה" in result and "1200" in result and "1500" in result
    print(f"PASS test_invalid_plan_rejected: {ok}")
    return ok


def test_food_logging_updates_bucket():
    reset_db()
    set_plan("Dana", 1200)
    result = log_food("Dana", "לחם", "carbs", 1.0)
    data = load_data()
    ok = data["participants"]["Dana"]["daily_portions"]["carbs"] == 1.0 and "נרשם" in result
    print(f"PASS test_food_logging_updates_bucket: {ok}")
    return ok


def test_recipe_calc():
    reset_db()
    result = check_recipe("פשטידה", 600, 2)
    ok = "300" in result and "שווה ערך" in result
    print(f"PASS test_recipe_calc: {ok}")
    return ok


def test_weight_history_added():
    reset_db()
    set_plan("Dana", 1500)
    result = log_weight("Dana", 68.2)
    data = load_data()
    ok = data["participants"]["Dana"]["weight_history"] == [68.2] and "שקילה" in result
    print(f"PASS test_weight_history_added: {ok}")
    return ok

def test_real_world_food_keyword_fallback():
    detected = detect_food_name("בוטנים")
    classified = classify_food("בוטנים", 1.0)
    ok = detected.get("category") == "fat" and classified.get("category") == "fat" and "בוטנים" in classified.get("message", "")
    print(f"PASS test_real_world_food_keyword_fallback: {ok}")
    return ok

def test_scenario_routes_both_harnesses():
    scenario_path = Path(ROOT) / "scenario.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    original_data_path = data_store.DATA_FILE
    original_history_dir = api_history.HISTORY_DIR
    original_memory_path = api_memory.MEMORY_PATH

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            api_history.HISTORY_DIR = temp_root / "history"
            api_memory.MEMORY_PATH = temp_root / "memory.json"

            for harness_name in ("api", "sdk"):
                data_store.DATA_FILE = str(temp_root / f"{harness_name}-database.json")
                data_store.save_data({"participants": {}})
                memory_state = {}
                sdk_agent = SDKDietAgent(offline=True)

                for session in scenario["sessions"]:
                    for turn in session["turns"]:
                        if harness_name == "api":
                            result = run_turn(
                                session["session_id"], session["user"],
                                turn["input"], memory_state,
                            )
                            tool_name = result["tool_name"]
                        else:
                            result = sdk_agent.handle(
                                session["session_id"], session["user"], turn["input"]
                            )
                            tool_name = result["tool_name"]
                        assert tool_name == turn["expected_tools"][0], (harness_name, turn, result)

                participant = data_store.load_data()["participants"]["Dana"]
                assert participant["plan"] == 1500
                assert participant["daily_portions"]["carbs"] == 1
                assert participant["daily_portions"]["protein"] == 1
                assert participant["weight_history"] == [68.2]
    finally:
        data_store.DATA_FILE = original_data_path
        api_history.HISTORY_DIR = original_history_dir
        api_memory.MEMORY_PATH = original_memory_path

    print("PASS test_scenario_routes_both_harnesses: True")
    return True


def run_all():
    checks = [
        test_plan_switch_ok(),
        test_invalid_plan_rejected(),
        test_food_logging_updates_bucket(),
        test_recipe_calc(),
        test_weight_history_added(),
        test_real_world_food_keyword_fallback(),
        test_scenario_routes_both_harnesses(),
    ]
    return all(checks)


if __name__ == "__main__":
    passed = run_all()
    print(f"OVERALL: {passed}")
    raise SystemExit(0 if passed else 1)
