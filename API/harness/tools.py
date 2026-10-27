import json
from shared.tools import set_plan, log_food, check_recipe, log_weight


def dispatch_tool(name, command, **kwargs):
    print(f"[API.harness.tools] Executing tool: {command} for {name}")
    if command == "set_plan":
        return set_plan(name, int(kwargs.get("plan_type", 1500)))
    if command == "log_food":
        return log_food(
            name=name,
            item_name=kwargs.get("item_name", ""),
            portion_type=kwargs.get("portion_type", "carbs"),
            count=float(kwargs.get("count", 1.0)),
        )
    if command == "check_recipe":
        return check_recipe(
            recipe_name=kwargs.get("recipe_name", ""),
            total_calories=float(kwargs.get("total_calories", 0.0)),
            num_servings=int(kwargs.get("num_servings", 1)),
        )
    if command == "log_weight":
        return log_weight(name, float(kwargs.get("weight", 0.0)))
    return {"error": True, "message": f"Unknown command: {command}"}
