import os


MODEL = os.environ.get("DIET_AGENT_MODEL", "claude-sonnet-4-6")
EFFORT = os.environ.get("DIET_AGENT_EFFORT", "medium")

PRICES_PER_MILLION = {
	"claude-sonnet-4-6": {
		"input": 3.0,
		"output": 15.0,
		"cache_read": 0.30,
		"cache_creation": 3.75,
	}
}


def estimate_cost_usd(usage, web_search_requests=0):
	prices = PRICES_PER_MILLION.get(MODEL)
	if prices is None:
		return None
	token_cost = sum(
		(usage.get(token_name, 0) or 0) * prices[price_name] / 1_000_000
		for token_name, price_name in (
			("input_tokens", "input"),
			("output_tokens", "output"),
			("cache_read_input_tokens", "cache_read"),
			("cache_creation_input_tokens", "cache_creation"),
		)
	)
	return token_cost + web_search_requests * 0.01
