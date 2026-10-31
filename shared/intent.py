import re

from shared.tools import detect_food_name


def parse_intent(user_input):
    text = (user_input or "").strip().lower()
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text)
    if not text:
        return None

    if "מה" in text and any(word in text for word in ("תוכנית", "תכנית", "רשם", "רשמ")):
        return {"command": "load_memory", "arguments": {}}
    if "מתכון" in text or "recipe" in text:
        if len(numbers) < 2:
            return None
        return {"command": "check_recipe", "arguments": {
            "recipe_name": "פשטידה",
            "total_calories": float(numbers[0].replace(",", ".")),
            "num_servings": int(numbers[1]),
        }}
    if ("תוכנית" in text or "תכנית" in text or "set_plan" in text) and numbers:
        return {"command": "set_plan", "arguments": {"plan_type": int(numbers[0])}}
    if any(word in text for word in ("שקל", "משקל", "weight")) and numbers:
        return {"command": "log_weight", "arguments": {
            "weight": float(numbers[0].replace(",", ".")),
        }}
    if any(word in text for word in ("רשום", "רשמי", "אכל", "log_food")):
        detected = detect_food_name(text)
        if detected.get("error"):
            return None
        portion_type = next(
            (category for category in ("carbs", "protein", "fat", "fruit", "treat") if category in text),
            detected["category"],
        )
        return {"command": "log_food", "arguments": {
            "item_name": detected["name"],
            "portion_type": portion_type,
            "count": float(numbers[0].replace(",", ".")) if numbers else 1.0,
        }}
    return None
