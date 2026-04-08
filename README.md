# CopilotKit + LangGraph agent (my-agent)

Demo **LangGraph** workflow (idea → confirm → plan → feedback) with **CopilotKit**, **Next.js** + Tailwind UI. The Python backend uses `**uv`**; the LangGraph CLI loads the graph from `main.py`.

**For AI / contributors:** see `[AGENTS.md](./AGENTS.md)` for routing, `AgentState`, and where to change when adding nodes.

## Requirements

- Python **3.12**
- [uv](https://docs.astral.sh/uv/) (package and virtualenv management)
- Node.js + npm (for the frontend)

## Backend setup

```bash
uv sync --group dev
```

Create a `.env` file in the repo root (the LangGraph CLI uses `env` from `langgraph.json`). Example variables:


| Variable         | Description                                                 |
| ---------------- | ----------------------------------------------------------- |
| `MODEL_NAME`     | OpenAI-compatible model id (default in code: `gpt-4o-mini`) |
| `OPENAI_API_KEY` | Provider API key (usually required for chat)                |
| `TAVILY_API_KEY` | Required if you use Tavily web search                       |


## Run the agent (LangGraph dev server)

```bash
npx @langchain/langgraph-cli dev --port 8123
```

Graph entry: `./main.py:graph` (declared in `langgraph.json`).

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

## Code quality (QA)

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pre-commit run --all-files
```

## Demo video

[Planning Agent Demo](https://drive.google.com/file/d/1i7-ahA5zLwoHRCft_JxxxB03MxKueJEK/view)