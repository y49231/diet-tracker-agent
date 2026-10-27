def estimate_tokens(text):
    if text is None:
        return 0
    return max(1, len(str(text).split()))


def create_usage_summary(input_text, output_text, cache_read=0, cache_write=0):
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return {
        "input": input_tokens,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "output": output_tokens,
        "total": input_tokens + output_tokens + cache_read + cache_write,
    }
