import asyncio
import time

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    ServerToolUseBlock,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
)

from SDK.tools import dispatch_tool
from SDK.tools import create_sdk_tools
from shared.agent_config import EFFORT, MODEL
from shared.intent import parse_intent


class SDKDietAgent:
    def __init__(self, offline=True, client_factory=ClaudeSDKClient):
        self.memory = {}
        self.offline = offline
        self.client_factory = client_factory
        self.clients = {}
        self.session_usage = {}

    async def start_session(self, session_id, user_name, context):
        tools = create_sdk_tools(user_name)
        server = create_sdk_mcp_server(name="diet_tracker", tools=tools)
        options = ClaudeAgentOptions(
            model=MODEL,
            effort=EFFORT,
            max_turns=8,
            max_budget_usd=1.0,
            tools=["WebSearch"],
            allowed_tools=["WebSearch", *[f"mcp__diet_tracker__{item.name}" for item in tools]],
            mcp_servers={"diet_tracker": server},
            strict_mcp_config=True,
            setting_sources=[],
            system_prompt=(
                "You are a diet tracking assistant. Reply in Hebrew. "
                "Use diet_tracker tools for state changes and saved status. "
                f"User context: {context}"
            ),
        )
        client = self.client_factory(options=options)
        await client.connect()
        self.clients[session_id] = client
        self.session_usage[session_id] = {}

    async def handle_async(self, session_id, user_name, user_input, context=None):
        if self.offline:
            intent = parse_intent(user_input)
            tool_name = intent["command"] if intent else None
            result = dispatch_tool(user_name, tool_name, **intent["arguments"]) if intent else "לא זוהתה פעולה מתאימה."
            return {"response": result, "tool_used": tool_name is not None, "tool_name": tool_name,
                    "tool_names": [tool_name] if tool_name else [], "usage": {}, "api_calls": 0,
                    "duration_ms": 0, "is_error": False}

        if session_id not in self.clients:
            await self.start_session(session_id, user_name, context or {})
        started = time.perf_counter()
        client = self.clients[session_id]
        await client.query(user_input)
        text_parts = []
        tool_names = []
        model_calls = 0
        result_message = None
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                model_calls += 1
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        name = block.name.rsplit("__", 1)[-1]
                        if name != "web_search":
                            tool_names.append(name)
                    elif isinstance(block, ServerToolUseBlock) and block.name == "WebSearch":
                        tool_names.append("web_search")
            elif isinstance(message, ResultMessage):
                result_message = message

        usage = result_message.usage or {} if result_message else {}
        total_usage = self.session_usage[session_id]
        turn_usage = {}
        for key in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
            turn_usage[key] = usage.get(key, 0) or 0
            total_usage[key] = total_usage.get(key, 0) + turn_usage[key]
        total_usage["total_tokens"] = total_usage.get("input_tokens", 0) + total_usage.get("output_tokens", 0)
        if result_message and result_message.total_cost_usd is not None:
            previous_cost = total_usage.get("last_reported_cost_usd", 0.0)
            total_usage["total_cost_usd"] = result_message.total_cost_usd
            turn_usage["total_cost_usd"] = max(0.0, result_message.total_cost_usd - previous_cost)
            total_usage["last_reported_cost_usd"] = result_message.total_cost_usd
        else:
            turn_usage["total_cost_usd"] = None
        turn_usage["total_tokens"] = turn_usage["input_tokens"] + turn_usage["output_tokens"]
        web_search_requests = usage.get("server_tool_use", {}).get("web_search_requests", 0) or 0
        turn_usage["web_search_requests"] = web_search_requests
        if result_message and result_message.total_cost_usd is not None:
            previous_cost = total_usage.get("last_reported_cost_usd", 0.0)
            total_usage["total_cost_usd"] = result_message.total_cost_usd
            turn_usage["total_cost_usd"] = max(0.0, result_message.total_cost_usd - previous_cost)
            total_usage["last_reported_cost_usd"] = result_message.total_cost_usd
        else:
            turn_usage["total_cost_usd"] = None
        return {
            "response": "\n".join(text_parts) or (result_message.result if result_message else ""),
            "tool_used": bool(tool_names), "tool_name": tool_names[0] if tool_names else None,
            "tool_names": tool_names, "usage": turn_usage,
            "session_usage": dict(total_usage), "api_calls": model_calls,
            "duration_ms": result_message.duration_ms if result_message else round((time.perf_counter() - started) * 1000),
            "is_error": result_message.is_error if result_message else False,
        }

    def handle(self, session_id, user_name, user_input):
        if not self.offline:
            raise RuntimeError("Live SDK runs must call handle_async() from an asyncio event loop.")
        intent = parse_intent(user_input)
        tool_name = intent["command"] if intent else None
        result = dispatch_tool(user_name, tool_name, **intent["arguments"]) if intent else "לא זוהתה פעולה מתאימה."
        return {"response": result, "tool_used": tool_name is not None, "tool_name": tool_name}

    async def close(self):
        for client in self.clients.values():
            await client.disconnect()
