"""After the idea is summarized, decide whether to plan or keep helping the user."""

import json
import re
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.types import Command

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState

_NODE_DIR = Path(__file__).resolve().parent
CONFIRM_PROMPT = load_prompt(_NODE_DIR)


def _last_human_text(state: AgentState) -> str:
    for m in reversed(state.get("messages") or []):
        if isinstance(m, HumanMessage):
            c = m.content
            if isinstance(c, str):
                return c.strip()
            if isinstance(c, list) and c:
                return str(c[0])
    return ""


async def confirmation_handler(
    state: AgentState,
    _config: RunnableConfig | None = None,
) -> Command:
    """Classify the user's reply after idea recap: enough to plan vs needs more help."""
    text = _last_human_text(state)

    model = ChatOpenAI(model=get_model_name(), temperature=0)
    json_hint = '\nRespond with JSON only: {"action":"plan"|"help"|"clarify","note":"short reason"}'
    sys = SystemMessage(content=CONFIRM_PROMPT + json_hint)
    structured = await model.ainvoke(
        [sys, HumanMessage(content=f"User message:\n{text or '(empty)'}")]
    )
    raw = structured.content if isinstance(structured.content, str) else str(structured.content)
    action = "clarify"
    try:
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            data = json.loads(m.group())
            action = data.get("action", "clarify")
    except json.JSONDecodeError:
        pass

    if action == "plan":
        return Command(
            goto="plan_node",
            update={"workflow_stage": "planning"},
        )
    if action == "help":
        return Command(
            goto="idea_helper",
            update={"workflow_stage": "awaiting_confirm"},
        )

    ask = AIMessage(
        content=(
            "I am not sure I understood. Please reply **yes** if the summary matches your idea "
            "and you are ready for a plan, or explain what is missing or wrong."
        )
    )
    return Command(goto=END, update={"messages": [ask]})
