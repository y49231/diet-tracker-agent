from collections import deque


def build_context(user_name, recent_history, memory_state):
    print(f"[API.harness.context] Building per-turn context for {user_name}")
    recent_events = list(recent_history)[-3:]
    user_memory = memory_state.get(user_name, {})
    relevant = {
        "user": user_name,
        "plan": user_memory.get("plan", 1500),
        "preferences": user_memory.get("preferences", {}),
        "recent_events": recent_events,
        "memory_summary": user_memory.get("summary", "no_saved_summary"),
    }
    return relevant
