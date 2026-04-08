from pathlib import Path

from copilotkit import CopilotKitState
from langchain_core.messages import SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt

_NODE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT = load_prompt(_NODE_DIR)


async def response_node(
    state: CopilotKitState,
    _config: RunnableConfig | None = None,
):
    copilotkit = state.get("copilotkit") or {}
    tools = copilotkit.get("actions", []) if isinstance(copilotkit, dict) else []

    llm = ChatOpenAI(model=get_model_name())
    model: Runnable = llm.bind_tools(tools) if tools else llm

    system_message = SystemMessage(content=SYSTEM_PROMPT)
    response = await model.ainvoke([system_message, *state["messages"]])
    return {"messages": response}
