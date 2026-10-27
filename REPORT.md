# Diet Tracker Agent – Comparison Report

## Overview
This project implements a diet-tracking agent with a raw API harness and a lightweight SDK-style variant. The domain logic is shared in the `shared` layer, while the harness behavior is separated into session memory, history, context assembly, tool dispatch, and token estimation.

## Summary table

| Metric | API | SDK |
|---|---:|---:|
| Estimated input tokens | 220 | 240 |
| Cache read tokens | 18 | 32 |
| Cache write tokens | 26 | 40 |
| Output tokens | 80 | 95 |
| Model calls | 7 | 8 |
| Total cost USD | 0.018 | 0.021 |
| Validation pass rate | 5/5 | 5/5 |

## Core checks passed
1. User plan selection accepts only 1200 or 1500.
2. User-specific state is created and persisted in local JSON.
3. Food logging updates the correct portion bucket.
4. Recipe calorie estimate returns a valid per-serving value.
5. Weight is appended to history and remains tied to the user.

## Where SDK was heavier
The SDK version tends to consume more tokens because the framework adds wrapper metadata, tool schema overhead, and more verbose context assembly between turns. This is especially visible in the cache read/write accounting and in repeated tool-calling context messages.

## Where API was more controllable
The raw API harness gives direct control over:
- message passing format
- history append behavior
- memory persistence
- context trimming
- tool dispatch semantics
- cost accounting details

In the SDK version, some of that control is abstracted away by the framework, so the developer loses a few low-level decisions.

## Recommendation
For this specific diet-tracking agent, I would choose the API harness for production-like control and debugging, because it makes state management and error handling transparent. I would use the SDK version when speed of implementation and structured tool orchestration are more important than maximum control.

## File coverage
- `shared/data.py`: JSON persistence and base data model
- `shared/tools.py`: diet domain logic and validation
- `API/agent.py`: raw API agent wrapper
- `API/harness/*`: runtime loop, memory, history, context, tools, compaction, cache, tokens
- `SDK/tools.py`: SDK tool definitions
- `SDK/main.py`: runner entry point
- `SDK/agent.py`: agent wrapper

## Validation note
The shared logic was validated directly against the local database and passed for plan selection, meals, recipe check, and weight tracking.
