import re

from shared.data import load_data, save_data

PLAN_LIMITS = {
    1500: {"carbs": 6, "protein": 5, "fat": 3, "fruit": 3, "treat": 1},
    1200: {"carbs": 4, "protein": 4, "fat": 3, "fruit": 3, "treat": 1}
}

FOOD_CATALOG = {
    "carbs": {
        "לחם פרוסה": {"unit": "פרוסה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 80},
        "אורז מבושל": {"unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 200},
        "תפוח גדול": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 95},
        "סוכר": {"unit": "כוס", "reference_amount": 1, "portion_units": 4, "calories_per_unit": 400},
        "מתוק": {"unit": "כפית", "reference_amount": 1, "portion_units": 0.25, "calories_per_unit": 20},
        "לחמניה": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1.5, "calories_per_unit": 130},
    },
    "protein": {
        "עוף": {"unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 180},
        "יוגורט": {"unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
        "טונה": {"unit": "פחית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 160},
        "ביצה": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 70},
    },
    "fat": {
        "אבוקדו": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 160},
        "שמן זית": {"unit": "כף", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 45},
        "אגוזים": {"unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 30},
    },
    "fruit": {
        "תפוח": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 95},
        "בננה": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 105},
        "אשכולית": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 70},
    },
    "treat": {
        "עוגייה": {"unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
        "שוקולד": {"unit": "ריבוע", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 120},
        "סוכר": {"unit": "כוס", "reference_amount": 1, "portion_units": 2, "calories_per_unit": 400},
    }
}

FOOD_ALIASES = {
    "בוטנים": {"category": "fat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 30},
    "אגוזים": {"category": "fat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 30},
    "שקדים": {"category": "fat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 45},
    "שמן": {"category": "fat", "unit": "כף", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 45},
    "חמאה": {"category": "fat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 35},
    "אבוקדו": {"category": "fat", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 160},
    "שוקולד": {"category": "treat", "unit": "ריבוע", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 120},
    "עוגייה": {"category": "treat", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
    "עוגיה": {"category": "treat", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
    "מאפין": {"category": "treat", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 180},
    "גלידה": {"category": "treat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 50},
    "סוכר": {"category": "treat", "unit": "כפית", "reference_amount": 1, "portion_units": 0.25, "calories_per_unit": 20},
    "לחם": {"category": "carbs", "unit": "פרוסה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 80},
    "לחמניה": {"category": "carbs", "unit": "יחידה", "reference_amount": 1, "portion_units": 1.5, "calories_per_unit": 130},
    "פיתה": {"category": "carbs", "unit": "יחידה", "reference_amount": 1, "portion_units": 1.5, "calories_per_unit": 140},
    "פסטה": {"category": "carbs", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 200},
    "אורז": {"category": "carbs", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 200},
    "קוסקוס": {"category": "carbs", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 180},
    "בורגול": {"category": "carbs", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 170},
    "תפוח": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 95},
    "בננה": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 105},
    "אשכולית": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 70},
    "תפוז": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 62},
    "אבטיח": {"category": "fruit", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 50},
    "אננס": {"category": "fruit", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 60},
    "קיווי": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 42},
    "אפרסק": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 57},
    "תות": {"category": "fruit", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 50},
    "עוף": {"category": "protein", "unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 180},
    "ביצה": {"category": "protein", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 70},
    "טונה": {"category": "protein", "unit": "פחית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 160},
    "יוגורט": {"category": "protein", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
    "גבינה": {"category": "protein", "unit": "פרוסה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 90},
    "סלמון": {"category": "protein", "unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 210},
    "דג": {"category": "protein", "unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 180},
    "בשר": {"category": "protein", "unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 220},
    "טופו": {"category": "protein", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 140},
    "חלב": {"category": "protein", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 120},
    "קוטג": {"category": "protein", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 110},
    "שיבולת שועל": {"category": "carbs", "unit": "כף", "reference_amount": 1, "portion_units": 0.25, "calories_per_unit": 25},
    "אטריות": {"category": "carbs", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 220},
    "חזה עוף": {"category": "protein", "unit": "מנת בינונית", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 170},
    "קציצה": {"category": "protein", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 150},
    "חביתה": {"category": "protein", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 110},
    "חומוס": {"category": "protein", "unit": "כף", "reference_amount": 1, "portion_units": 0.5, "calories_per_unit": 35},
    "פלאפל": {"category": "protein", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 170},
    "סלט": {"category": "fruit", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 60},
    "עגבנייה": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 20},
    "מלפפון": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 15},
    "גזר": {"category": "fruit", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 35},
    "סופגניה": {"category": "treat", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 240},
    "בייגל": {"category": "carbs", "unit": "יחידה", "reference_amount": 1, "portion_units": 1.5, "calories_per_unit": 220},
    "כריך": {"category": "carbs", "unit": "יחידה", "reference_amount": 1, "portion_units": 1.5, "calories_per_unit": 300},
    "תפוח אדמה": {"category": "carbs", "unit": "יחידה", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 130},
    "מרק": {"category": "protein", "unit": "כוס", "reference_amount": 1, "portion_units": 1, "calories_per_unit": 120},
}

FOOD_NAME_LOOKUP = {}
for category, items in FOOD_CATALOG.items():
    for item_name, meta in items.items():
        FOOD_NAME_LOOKUP[item_name] = {"category": category, **meta}
for item_name, meta in FOOD_ALIASES.items():
    FOOD_NAME_LOOKUP[item_name] = meta


def _normalize_food_name(item_name: str) -> str:
    text = item_name.strip().lower()
    return re.sub(r"\s+", " ", text)


def detect_food_name(item_name: str):
    if not item_name:
        return {"error": True, "message": "שם המזון ריק."}

    normalized = _normalize_food_name(item_name)
    for food_name, details in FOOD_NAME_LOOKUP.items():
        candidate = _normalize_food_name(food_name)
        if normalized == candidate or normalized in candidate or candidate in normalized:
            return {"category": details["category"], "name": food_name, **details}

    candidate_keywords = [
        "עוף", "ביצה", "טונה", "יוגורט", "גבינה", "סלמון", "דג", "טופו", "חלב", "קוטג",
        "תפוח", "בננה", "אשכולית", "תפוז", "אבטיח", "אננס", "קיווי", "אפרסק", "תות",
        "שוקולד", "עוגיה", "עוגייה", "מאפין", "גלידה", "בוטנים", "אגוזים", "שקדים", "אבוקדו",
        "לחם", "לחמניה", "פיתה", "אורז", "פסטה", "קוסקוס", "בורגול", "שיבולת שועל", "סוכר"
    ]
    for keyword in candidate_keywords:
        if keyword in normalized:
            alias = FOOD_ALIASES.get(keyword)
            if alias:
                return {"category": alias["category"], "name": keyword, **alias}

    return {"error": True, "message": f"לא זוהה מאכל: {item_name}."}


def classify_food(item_name: str, amount: float = 1.0, plan_type: int = 1500):
    detected = detect_food_name(item_name)
    if detected.get("error"):
        return detected

    category = detected["category"]
    calories_per_unit = float(detected["calories_per_unit"])
    unit = detected["unit"]
    portion_equivalent = round((amount / detected["reference_amount"]) * detected["portion_units"], 2)
    estimated_total_calories = round(amount * calories_per_unit, 1)

    return {
        "food_name": detected["name"],
        "category": category,
        "unit": unit,
        "amount": amount,
        "calories_per_unit": calories_per_unit,
        "portion_equivalent": portion_equivalent,
        "estimated_total_calories": estimated_total_calories,
        "plan_type": plan_type,
        "message": f"הזוהה {detected['name']} כ-{category}. כמות {amount} {unit} = {portion_equivalent} מנות. קלוריות משוערות: {estimated_total_calories}."
    }


def get_participant_data(participants, name):
    if name not in participants:
        participants[name] = {
            "plan": 1500,
            "daily_portions": {
                "carbs": 0,
                "protein": 0,
                "fat": 0,
                "fruit": 0,
                "treat": 0
            },
            "weight_history": []
        }
    return participants[name]

def set_plan(name: str, plan_type: int) -> str:
    if plan_type not in [1200, 1500]:
        return "שגיאה: יש לבחור תוכנית של 1200 או 1500 קלוריות בלבד."
    
    data = load_data()
    participant = get_participant_data(data["participants"], name)
    participant["plan"] = plan_type
    save_data(data)
    
    return f"התוכנית עבור {name} עודכנה בהצלחה ל-{plan_type} קלוריות."

def estimate_food_portion(portion_type: str, item_name: str, amount: float = 1.0, unit: str = "יחידה") -> dict:
    detected = detect_food_name(item_name)
    if detected.get("error"):
        return detected
    if portion_type is None or portion_type not in FOOD_CATALOG:
        portion_type = detected["category"]

    item = FOOD_CATALOG.get(portion_type, {}).get(detected["name"])
    if item is None:
        item = FOOD_ALIASES.get(detected["name"])
    if item is None:
        return {"error": True, "message": f"פריט לא נמצא בקטגוריה {portion_type}: {item_name}."}

    reference = float(item["reference_amount"])
    portion_units = float(item["portion_units"])
    calories = float(item["calories_per_unit"])
    equivalent = (amount / reference) * portion_units
    total_calories = amount * calories

    return {
        "item_name": item_name,
        "portion_type": portion_type,
        "amount": amount,
        "unit": unit or item["unit"],
        "equivalent_portions": round(equivalent, 2),
        "estimated_calories": round(total_calories, 1),
        "message": f"{amount} {unit or item['unit']} של {item_name} = {round(equivalent, 2)} מנות {portion_type}."
    }


def log_food(name: str, item_name: str, portion_type: str = None, count: float = 1.0) -> str:
    data = load_data()
    participant = get_participant_data(data["participants"], name)
    
    current_plan = participant.get("plan", 1500)
    limits = PLAN_LIMITS.get(current_plan, PLAN_LIMITS[1500])

    detected = detect_food_name(item_name)
    if detected.get("error"):
        return detected["message"]

    portion_type = portion_type or detected["category"]
    if portion_type not in limits:
        return f"סוג מנה לא מוכר: {portion_type}. סוגים אפשריים: carbs, protein, fat, fruit, treat."

    estimate = estimate_food_portion(portion_type, item_name, count, "יחידה")
    if estimate.get("error"):
        return estimate["message"]

    participant["daily_portions"][portion_type] = participant["daily_portions"].get(portion_type, 0) + estimate["equivalent_portions"]
    save_data(data)
    
    used = participant["daily_portions"][portion_type]
    max_allowed = limits[portion_type]
    remaining = max_allowed - used
    
    return f"נרשם עבור {name}: {item_name} ({count} יחידות). שווה ל-{estimate['equivalent_portions']} מנות {portion_type}. הוערך ב-{estimate['estimated_calories']} קלוריות. ניצול עד כה: {used}/{max_allowed}. נותרו: {remaining} מנות."

def check_recipe(recipe_name: str, total_calories: float, num_servings: int) -> str:
    if num_servings <= 0:
        return "שגיאה: מספר המנות חייב להיות גדול מ-0."
    
    cal_per_serving = total_calories / num_servings
    portions_equivalent = round(cal_per_serving / 80.0, 1)
    
    return (f"במתכון '{recipe_name}' עבור {num_servings} מנות/פרוסות:\n"
            f"- כל פרוסה מכילה כ-{cal_per_serving:.0f} קלוריות.\n"
            f"- שווה ערך לכ-{portions_equivalent} מנות בתפריט.")

def log_weight(name: str, weight: float) -> str:
    data = load_data()
    participant = get_participant_data(data["participants"], name)
    
    history = participant.get("weight_history", [])
    history.append(weight)
    participant["weight_history"] = history
    save_data(data)
    
    if len(history) == 1:
        return f"שקילה ראשונה נרשמה עבור {name}: {weight} ק\"ג."
    
    start_weight = history[0]
    prev_weight = history[-2]
    diff_from_prev = prev_weight - weight
    total_drop = start_weight - weight
    
    return (f"שקילה נרשמה עבור {name}: {weight} ק\"ג.\n"
            f"- שינוי מהשקילה הקודמת: {diff_from_prev:+.1f} ק\"ג.\n"
            f"- סך ירידה מצטברת: {total_drop:.1f} ק\"ג.")