# Diet Tracker Agent – Comparison Report

## Overview
This project compares a direct Anthropic Messages API harness with a Claude Agent SDK harness. Both use the same local diet-tracking tools and shared model/effort settings.

## Scenario

`scenario.json` contains seven turns across two sessions. The API runner and SDK runner default to live provider calls. Use `--offline` for local deterministic tests. Both runners accept a temporary database path through `--data`; the API runner also accepts isolated history and memory paths.

The saved results in `results/` currently have `mode: offline`; they validate routing and state only. They are not provider measurements and must not be used to compare token usage, latency, or cost.

## Validation

Run the local checks with `python tests/offline_checks.py`. The tests cover the shared domain functions and verify all seven expected tool selections and final state in both local harness paths without making provider calls.

Live token counts, provider cost, and latency are recorded by the runners when credentials are configured. Those values must be collected from a live run before making a measured comparison.

## Comparison Notes

- The API harness explicitly runs the Messages API tool-use round trip and records per-response usage.
- The SDK harness uses a persistent `ClaudeSDKClient` per scenario session, an in-process MCP server for diet tools, and Claude Code's WebSearch tool.
- Both are configured with the same model and effort values in `shared/agent_config.py`.
- SDK live runs have a $1 max budget configured. API web search is limited to one search per request.
- A live run has not been recorded: the local environment had no Anthropic API key, Claude Code OAuth token, or Claude CLI available during validation.

## Setup

Install dependencies from `requirements.txt`, configure Anthropic API authentication and Claude Code authentication locally, then run each entry point with `scenario.json`. Results and their associated database/history files are isolated under `results/*_state/` by default. To run only deterministic local checks, use `--offline` or `python tests/offline_checks.py`. Never commit API keys or local credentials.
