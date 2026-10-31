import sys
import os
import time

# הוספת תיקיית האם למסלול החיפוש של פייתון
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from anthropic import Anthropic

from API.harness.tools import dispatch_tool
from shared.agent_config import EFFORT, MODEL, estimate_cost_usd


TOOLS = [
    {
        "name": "set_plan",
        "description": "Set the user's daily calorie plan to 1200 or 1500.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_type": {"type": "integer", "enum": [1200, 1500]}},
            "required": ["plan_type"],
        },
    },
    {
        "name": "log_food",
        "description": "Log a food item and portion count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_name": {"type": "string"},
                "portion_type": {"type": "string", "enum": ["carbs", "protein", "fat", "fruit", "treat"]},
                "count": {"type": "number"},
            },
            "required": ["item_name", "portion_type", "count"],
        },
    },
    {
        "name": "check_recipe",
        "description": "Calculate calories per serving for a recipe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipe_name": {"type": "string"},
                "total_calories": {"type": "number"},
                "num_servings": {"type": "integer", "minimum": 1},
            },
            "required": ["recipe_name", "total_calories", "num_servings"],
        },
    },
    {
        "name": "log_weight",
        "description": "Record a weight in kilograms.",
        "input_schema": {
            "type": "object",
            "properties": {"weight": {"type": "number", "exclusiveMinimum": 0}},
            "required": ["weight"],
        },
    },
    {
        "name": "load_memory",
        "description": "Read the user's current plan and logged portions.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]
WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 1}

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


class MessagesAPIAgent:
    def __init__(self, client=None):
        self.client = client or Anthropic()

    def handle(self, name, user_input, context):
        started = time.perf_counter()
        messages = [{"role": "user", "content": user_input}]
        usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
        tool_names = []
        tool_calls = []
        web_search_requests = 0
        calls = 0
        answer = ""

        while calls < 8:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=1200,
                system=[{
                    "type": "text",
                    "text": (
                        "You are a diet tracking assistant. Answer in Hebrew. "
                        "Use the supplied tools for all changes and saved-status questions. "
                        f"User context: {context}"
                    ),
                    "cache_control": {"type": "ephemeral"},
                }],
                tools=[*TOOLS[:-1], {**TOOLS[-1], "cache_control": {"type": "ephemeral"}}, WEB_SEARCH],
                messages=messages,
                output_config={"effort": EFFORT},
            )
            calls += 1
            for key in usage:
                usage[key] += getattr(response.usage, key, 0) or 0
            messages.append({"role": "assistant", "content": response.content})
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            server_searches = [
                block for block in response.content
                if block.type == "server_tool_use" and block.name == "web_search"
            ]
            web_search_requests += len(server_searches)
            for block in server_searches:
                tool_names.append("web_search")
                tool_calls.append({"tool": "web_search", "input": block.input, "server_side": True})
            answer = "\n".join(block.text for block in response.content if block.type == "text")
            if not tool_uses and response.stop_reason != "pause_turn":
                break

            results = []
            for tool_use in tool_uses:
                tool_names.append(tool_use.name)
                result = dispatch_tool(name, tool_use.name, **tool_use.input)
                tool_calls.append({"tool": tool_use.name, "input": tool_use.input, "result": str(result)})
                results.append({"type": "tool_result", "tool_use_id": tool_use.id, "content": str(result)})
            if results:
                messages.append({"role": "user", "content": results})

        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        usage["web_search_requests"] = web_search_requests
        usage["total_cost_usd"] = estimate_cost_usd(usage, web_search_requests)
        return {
            "response": answer,
            "tool_names": tool_names,
            "tool_calls": tool_calls,
            "usage": usage,
            "api_calls": calls,
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "model": MODEL,
            "effort": EFFORT,
        }

if __name__ == "__main__":
    agent = DietAgentHarness()
    
    # בדיקה מקומית להרצת הכלים
    print(agent.handle_request("ישראל", "set_plan", plan_type=1500))
    print(agent.handle_request("ישראל", "log_food", item_name="לחם פרוסה", portion_type="carbs", count=1.0))
    print(agent.handle_request("ישראל", "log_weight", weight=80.5))