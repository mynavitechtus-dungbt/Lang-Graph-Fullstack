"""Emit plan as real LangChain tool_calls so CopilotKit can complete the tool round-trip."""

import uuid
from pathlib import Path

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState

_NODE_DIR = Path(__file__).resolve().parent
PLAN_PROMPT = load_prompt(_NODE_DIR)


async def plan_node(
    state: AgentState,
    _config: RunnableConfig | None = None,
):
    """Produce a Markdown plan and request generative UI via assistant tool_calls."""
    model = ChatOpenAI(model=get_model_name(), temperature=0.3)
    system_message = SystemMessage(content=PLAN_PROMPT)
    plan_msg = await model.ainvoke([system_message, *state["messages"]])
    body = (
        plan_msg.content
        if isinstance(plan_msg.content, str)
        else str(plan_msg.content)
    )

    q = (
        "Do you approve this plan? Choose Yes to continue or No to request "
        "changes."
    )
    tc_md = str(uuid.uuid4())
    tc_btn = str(uuid.uuid4())
    ack = AIMessage(
        content=(
            "The plan is shown above as Markdown, with **Yes** / **No** buttons. "
            "You can also type **yes** or **no** in the chat."
        ),
        tool_calls=[
            {
                "name": "renderMarkdown",
                "args": {
                    "title": "Your plan",
                    "markdown": body,
                },
                "id": tc_md,
            },
            {
                "name": "showPlanApproval",
                "args": {"question": q},
                "id": tc_btn,
            },
        ],
    )
    return {
        "messages": [ack],
        "workflow_stage": "awaiting_plan_feedback",
    }
