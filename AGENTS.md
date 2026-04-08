# Agent instructions (Cursor / contributors)

This file describes how the **LangGraph + CopilotKit** backend is structured so edits stay consistent. For Python style (Ruff, mypy), see `.cursor/rules/python-quality.mdc`.

## Stack

- **Python 3.12**, **`uv`** for dependencies (`pyproject.toml`, `uv.lock`).
- **LangGraph** graph exported as `graph` from `main.py` (see `langgraph.json`).
- **CopilotKit** state: `AgentState` extends `CopilotKitState` (`nodes/state.py`).
- **LLM**: `langchain-openai`; model id from `MODEL_NAME` (default `gpt-4o-mini`) in `nodes/llm_config.py`.
- **Optional web search**: Tavily — requires `TAVILY_API_KEY` (`nodes/tools/web_search.py`).

## Entry and routing

- Graph is built in `main.py` with `StateGraph(AgentState)`.
- `START` uses `route_entry`, which reads `state["workflow_stage"]` via `coerce_workflow_stage()` (`workflow_stage.py`).
- When adding a stage or node: update `WorkflowStage`, `route_entry` mapping, `add_node` / `add_edge` / `add_conditional_edges` as needed, and keep stage string values aligned with `WorkflowStage` enum members.

## Layout

| Area | Role |
|------|------|
| `main.py` | Graph definition, `route_entry`, compiled `graph` |
| `workflow_stage.py` | `WorkflowStage` enum, `coerce_workflow_stage`, next/back sets |
| `nodes/state.py` | `AgentState` TypedDict |
| `nodes/*/node.py` | One node module per logical step (idea, confirmation, plan, feedback, …) |
| `nodes/tools/` | Tools (e.g. web search) |
| `nodes/llm_config.py` | Model name resolution |

## Conventions

- Prefer extending existing nodes and `AgentState` fields over duplicating flows.
- After changing Python: run `uv run ruff check .`, `uv run ruff format .`, and `uv run mypy .` (or `uv run pre-commit run --all-files`).
- Do not commit secrets; use `.env` locally (see `README.md`).

## Local run (backend)

From repo root: `npx @langchain/langgraph-cli dev --port 8123` (config in `langgraph.json`).
