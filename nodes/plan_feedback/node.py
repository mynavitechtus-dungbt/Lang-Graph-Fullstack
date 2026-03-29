import json
import re
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.types import Command

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState

_NODE_DIR = Path(__file__).resolve().parent
FB_PROMPT = load_prompt(_NODE_DIR)


def _last_human_text(state: AgentState) -> str:
    for m in reversed(state.get("messages") or []):
        if isinstance(m, HumanMessage):
            c = m.content
            if isinstance(c, str):
                return c.strip()
            if isinstance(c, list) and c:
                return str(c[0])
    return ""


async def plan_feedback_handler(state: AgentState) -> Command:
    """Handle approval or revision request after the plan is shown."""
    text = _last_human_text(state)

    model = ChatOpenAI(model=get_model_name(), temperature=0)
    sys = SystemMessage(
        content=FB_PROMPT
        + '\nRespond with JSON only: {"action":"approve"|"revise"|"unclear","note":"..."}'
    )
    structured = await model.ainvoke(
        [sys, HumanMessage(content=f"User message:\n{text or '(empty)'}")]
    )
    raw = structured.content if isinstance(structured.content, str) else str(structured.content)
    action = "unclear"
    try:
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            data = json.loads(m.group())
            action = data.get("action", "unclear")
    except json.JSONDecodeError:
        tl = text.lower()
        if re.match(r"^(yes|y|đúng|ok|approve|đồng ý|chốt)\b", tl):
            action = "approve"
        elif re.match(r"^(no|n|chưa|reject)\b", tl):
            action = "revise"

    if action == "approve":
        done = AIMessage(
            content=(
                "**Plan saved.** For this demo, your plan is treated as uploaded to **Google Drive** "
                "(no real file upload in this environment). You can copy the Markdown from the panel above anytime."
            )
        )
        return Command(
            goto=END,
            update={"messages": [done], "workflow_stage": "completed"},
        )

    if action == "revise":
        ask = AIMessage(
            content=(
                "What would you like to **add, remove, or change** in the plan? "
                "Reply with a short list; your next message will be used to regenerate the plan."
            )
        )
        return Command(
            goto=END,
            update={"messages": [ask], "workflow_stage": "plan_revision"},
        )

    clarify = AIMessage(
        content=(
            "Please type **yes** if you approve the plan (we will show it as saved to Google Drive), "
            "or **no** and describe what to change."
        )
    )
    return Command(goto=END, update={"messages": [clarify]})
