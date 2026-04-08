from pathlib import Path

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState
from nodes.tools.web_search import web_search

_NODE_DIR = Path(__file__).resolve().parent
HELP_PROMPT = load_prompt(_NODE_DIR)


async def idea_helper_node(
    state: AgentState,
    _config: RunnableConfig | None = None,
):
    name = get_model_name()
    bound = ChatOpenAI(model=name).bind_tools([web_search])
    plain = ChatOpenAI(model=name)
    system_message = SystemMessage(content=HELP_PROMPT)
    response = await bound.ainvoke([system_message, *state["messages"]])
    if not getattr(response, "tool_calls", None):
        return {"messages": response}

    tool_messages: list[ToolMessage] = []
    for tc in response.tool_calls:
        if tc["name"] == "web_search":
            q = tc["args"].get("query", "") if isinstance(tc["args"], dict) else ""
            out = await web_search.ainvoke({"query": q})
            tool_messages.append(ToolMessage(content=out, tool_call_id=tc["id"], name="web_search"))
    second = await plain.ainvoke([system_message, *state["messages"], response, *tool_messages])
    return {"messages": [response, *tool_messages, second]}
