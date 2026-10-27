from API.harness.history import append_history, load_history
from API.harness.memory import remember_user, get_user_memory
from API.harness.context import build_context
from API.harness.tools import dispatch_tool
from API.harness.tokens import create_usage_summary


def run_turn(session_id, user_name, user_input, memory_state):
    print(f"[API.harness.loop] Starting turn for session {session_id}")
    recent_history = load_history(session_id)
    context = build_context(user_name, recent_history, memory_state)
    tool_result = None
    tool_name = None

    if "set_plan" in user_input.lower():
        tool_name = "set_plan"
        tool_result = dispatch_tool(user_name, "set_plan", plan_type=1200)
    elif "log_food" in user_input.lower() or "אכל" in user_input.lower():
        tool_name = "log_food"
        tool_result = dispatch_tool(user_name, "log_food", item_name="לחם", portion_type="carbs", count=1.0)
    elif "שקל" in user_input.lower() or "weight" in user_input.lower():
        tool_name = "log_weight"
        tool_result = dispatch_tool(user_name, "log_weight", weight=70.0)
    elif "recipe" in user_input.lower() or "מתכון" in user_input.lower():
        tool_name = "check_recipe"
        tool_result = dispatch_tool(user_name, "check_recipe", recipe_name="פשטידה", total_calories=600, num_servings=2)

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
        "usage": create_usage_summary(user_input, str(tool_result), cache_read=0, cache_write=2),
        "stop_reason": "tool_use" if tool_name else "done",
    }
