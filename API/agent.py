import sys
import os

# הוספת תיקיית האם למסלול החיפוש של פייתון
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from shared.tools import set_plan, log_food, check_recipe, log_weight

class DietAgentHarness:
    """מעטפת (Harness) להפעלת הסוכן וניהול הפעולות עבור המשתתפים."""
    
    def handle_request(self, name: str, command: str, **kwargs) -> str:
        if command == "set_plan":
            return set_plan(name, kwargs.get("plan_type", 1500))
        elif command == "log_food":
            return log_food(
                name=name,
                item_name=kwargs.get("item_name", ""),
                portion_type=kwargs.get("portion_type", "carbs"),
                count=kwargs.get("count", 1.0)
            )
        elif command == "check_recipe":
            return check_recipe(
                recipe_name=kwargs.get("recipe_name", ""),
                total_calories=kwargs.get("total_calories", 0.0),
                num_servings=kwargs.get("num_servings", 1)
            )
        elif command == "log_weight":
            return log_weight(name, kwargs.get("weight", 0.0))
        else:
            return f"פקודה לא מוכרת: {command}"

if __name__ == "__main__":
    agent = DietAgentHarness()
    
    # בדיקה מקומית להרצת הכלים
    print(agent.handle_request("ישראל", "set_plan", plan_type=1500))
    print(agent.handle_request("ישראל", "log_food", item_name="לחם פרוסה", portion_type="carbs", count=1.0))
    print(agent.handle_request("ישראל", "log_weight", weight=80.5))