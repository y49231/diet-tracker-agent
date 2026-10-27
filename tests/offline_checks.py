import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.data import load_data, save_data
from shared.tools import set_plan, log_food, check_recipe, log_weight, detect_food_name, classify_food


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


def run_all():
    checks = [
        test_plan_switch_ok(),
        test_invalid_plan_rejected(),
        test_food_logging_updates_bucket(),
        test_recipe_calc(),
        test_weight_history_added(),
        test_real_world_food_keyword_fallback(),
    ]
    return all(checks)


if __name__ == "__main__":
    passed = run_all()
    print(f"OVERALL: {passed}")
    raise SystemExit(0 if passed else 1)
