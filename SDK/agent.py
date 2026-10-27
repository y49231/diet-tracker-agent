from SDK.tools import dispatch_tool


class SDKDietAgent:
    # replaces: API/agent.py
    def __init__(self):
        self.memory = {}

    def handle(self, session_id, user_name, user_input):
        text = (user_input or "").lower()
        if "1200" in text or "1500" in text:
            plan = 1200 if "1200" in text else 1500
            result = dispatch_tool(user_name, "set_plan", plan_type=plan)
        elif "לחם" in user_input or "carbs" in text:
            result = dispatch_tool(user_name, "log_food", item_name="לחם", portion_type="carbs", count=1.0)
        elif "שקל" in user_input or "weight" in text:
            result = dispatch_tool(user_name, "log_weight", weight=68.2)
        elif "מתכון" in user_input or "recipe" in text:
            result = dispatch_tool(user_name, "check_recipe", recipe_name="פשטידה", total_calories=600, num_servings=2)
        else:
            result = "הבנתי; אפשר לעדכן את תכנית התזונה או לרשום מנה."

        self.memory.setdefault(user_name, {})
        self.memory[user_name]["last_session"] = session_id
        self.memory[user_name]["summary"] = "diet session active"
        return {"response": result, "tool_used": True}
