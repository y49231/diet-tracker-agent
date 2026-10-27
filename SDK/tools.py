from shared.tools import set_plan, log_food, check_recipe, log_weight

TOOL_DEFS = [
    {
        "name": "set_plan",
        "description": "Set the user's daily calorie plan to 1200 or 1500.",
        "parameters": {"plan_type": {"type": "integer", "enum": [1200, 1500]}},
    },
    {
        "name": "log_food",
        "description": "Log a food entry into a portion bucket.",
        "parameters": {
            "item_name": {"type": "string"},
            "portion_type": {"type": "string"},
            "count": {"type": "number"},
        },
    },
    {
        "name": "check_recipe",
        "description": "Estimate calories and equivalent servings for a recipe.",
        "parameters": {
            "recipe_name": {"type": "string"},
            "total_calories": {"type": "number"},
            "num_servings": {"type": "integer"},
        },
    },
    {
        "name": "log_weight",
        "description": "Log the user's weight.",
        "parameters": {"weight": {"type": "number"}},
    },
]


def dispatch_tool(user_name, command, **kwargs):
    # replaces: API/harness/tools.py
    if command == "set_plan":
        return set_plan(user_name, int(kwargs.get("plan_type", 1500)))
    if command == "log_food":
        return log_food(
            user_name,
            kwargs.get("item_name", ""),
            kwargs.get("portion_type", "carbs"),
            float(kwargs.get("count", 1.0)),
        )
    if command == "check_recipe":
        return check_recipe(
            kwargs.get("recipe_name", ""),
            float(kwargs.get("total_calories", 0.0)),
            int(kwargs.get("num_servings", 1)),
        )
    if command == "log_weight":
        return log_weight(user_name, float(kwargs.get("weight", 0.0)))
    return {"error": True, "message": f"Unknown command: {command}"}
