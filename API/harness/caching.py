CACHE = {}


def cache_get(key):
    print(f"[API.harness.caching] cache lookup: {key}")
    return CACHE.get(key)


def cache_set(key, value):
    print(f"[API.harness.caching] cache write: {key}")
    CACHE[key] = value
    return value


def cache_clear():
    print("[API.harness.caching] cache cleared")
    CACHE.clear()
