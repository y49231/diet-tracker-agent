import re

from API.harness.history import append_history, load_history
from API.harness.memory import remember_user, get_user_memory
from API.harness.context import build_context
from API.harness.tools import dispatch_tool
from API.harness.tokens import create_usage_summary
from shared.tools import detect_food_name
from API.agent import MessagesAPIAgent


def run_turn(session_id, user_name, user_input, memory_state, agent=None):
    print(f"[API.harness.loop] Starting turn for session {session_id}")
    recent_history = load_history(session_id)
    context = build_context(user_name, recent_history, memory_state)
    tool_result = None
    tool_name = None

    text = user_input.lower()
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text)

    if agent is not None:
        outcome = agent.handle(user_name, user_input, context)
        tool_name = outcome["tool_names"][0] if outcome["tool_names"] else None
        tool_result = outcome["response"]
        usage = outcome["usage"]
        api_calls = outcome["api_calls"]
        duration_ms = outcome["duration_ms"]
        tool_names = outcome["tool_names"]
        tool_calls = outcome["tool_calls"]
    elif ("תוכנית" in text or "תכנית" in text or "set_plan" in text) and numbers:
        tool_name = "set_plan"
        tool_result = dispatch_tool(user_name, "set_plan", plan_type=int(numbers[0]))
    elif "מתכון" in text or "recipe" in text:
        if len(numbers) >= 2:
            tool_name = "check_recipe"
            tool_result = dispatch_tool(
                user_name, "check_recipe", recipe_name="פשטידה",
                total_calories=float(numbers[0].replace(",", ".")),
                num_servings=int(numbers[1]),
            )
    elif any(word in text for word in ("שקל", "משקל", "weight")) and numbers:
        tool_name = "log_weight"
        tool_result = dispatch_tool(
            user_name, "log_weight", weight=float(numbers[0].replace(",", "."))
        )
    elif any(word in text for word in ("מהי התוכנית", "מה התוכנית", "מהי התכנית", "מה התכנית")):
        tool_name = "load_memory"
        tool_result = dispatch_tool(user_name, "load_memory")
    elif any(word in text for word in ("רשום", "רשמי", "אכל", "log_food")):
        detected = detect_food_name(user_input)
        if detected.get("error"):
            tool_result = detected["message"]
        else:
            amount = float(numbers[0].replace(",", ".")) if numbers else 1.0
            portion_type = next(
                (category for category in ("carbs", "protein", "fat", "fruit", "treat") if category in text),
                detected["category"],
            )
            tool_name = "log_food"
            tool_result = dispatch_tool(
                user_name, "log_food", item_name=detected["name"],
                portion_type=portion_type, count=amount,
            )
    if agent is None:
        usage = create_usage_summary(user_input, str(tool_result), cache_read=0, cache_write=0)
        api_calls = 0
        duration_ms = 0
        tool_names = [tool_name] if tool_name else []
        tool_calls = []

    message = {
        "session_id": session_id,
        "user": user_name,
        "input": user_input,
        "context": context,
        "tool": tool_name,
        "tool_result": tool_result,
    }
    append_history(session_id, message)

    memory_state.setdefault(user_name, {})
    memory_state[user_name]["summary"] = "user profile exists and meal tracking is active"
    remember_user(user_name, memory_state[user_name])

    return {
        "response": tool_result if isinstance(tool_result, str) else "Tool executed successfully.",
        "tool_name": tool_name,
        "tool_names": tool_names,
        "tool_calls": tool_calls,
        "usage": usage,
        "api_calls": api_calls,
        "duration_ms": duration_ms,
        "model": outcome.get("model") if agent is not None else None,
        "effort": outcome.get("effort") if agent is not None else None,
        "stop_reason": "tool_use" if tool_name else "done",
    }
