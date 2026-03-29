from pathlib import Path

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from copilotkit import CopilotKitState

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt

_NODE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT = load_prompt(_NODE_DIR)


async def response_node(
    state: CopilotKitState,
    _config: RunnableConfig | None = None,
):
    copilotkit = state.get("copilotkit") or {}
    tools = (
        copilotkit.get("actions", []) if isinstance(copilotkit, dict) else []
    )

    model = ChatOpenAI(model=get_model_name())
    if tools:
        model = model.bind_tools(tools)

    system_message = SystemMessage(content=SYSTEM_PROMPT)
    response = await model.ainvoke([system_message, *state["messages"]])
    return {"messages": response}
