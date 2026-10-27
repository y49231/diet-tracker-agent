def summarize_history(history):
    print("[API.harness.compaction] Summarizing history")
    if not history:
        return "No prior history."
    summary = []
    for item in history[-5:]:
        summary.append(item.get("tool", "message"))
    return "; ".join(summary)
