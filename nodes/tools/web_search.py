"""Web search for the idea-helper step (Tavily API)."""

import os

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for facts, examples, or best practices.

    Use when the user needs up-to-date or external context.
    """
    if not os.environ.get("TAVILY_API_KEY"):
        return "Search is unavailable: set TAVILY_API_KEY in the environment (.env)."
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Search is unavailable (missing tavily-python)."
    try:
        client = TavilyClient()
        resp = client.search(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"
    results = resp.get("results") or []
    if not results:
        answer = resp.get("answer")
        if answer:
            return f"Summary: {answer}\n(No linked results returned.)"
        return "No results found."
    lines = []
    for r in results:
        title = r.get("title", "")
        content = (r.get("content") or "")[:500]
        url = r.get("url", "")
        lines.append(f"- {title}: {content} ({url})")
    return "\n".join(lines)
