"""Helpers for LangChain message lists sent to OpenAI-compatible chat APIs."""

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage


def ensure_openai_tool_roundtrip(messages: list[BaseMessage]) -> list[BaseMessage]:
    """OpenAI rejects requests where an assistant message has ``tool_calls`` but one or
    more ``tool_call_id`` values never get a ``ToolMessage``. CopilotKit / LangGraph
    state can contain incomplete rounds (e.g. UI tools not finished). This appends
    placeholder tool replies for any missing ids so the API accepts the history.
    """
    out: list[BaseMessage] = []
    i = 0
    while i < len(messages):
        m = messages[i]
        tool_calls = getattr(m, "tool_calls", None) if isinstance(m, AIMessage) else None
        if isinstance(m, AIMessage) and tool_calls:
            out.append(m)
            required = [tc["id"] for tc in tool_calls if tc.get("id")]
            name_by_id = {tc["id"]: (tc.get("name") or "tool") for tc in tool_calls if tc.get("id")}
            i += 1
            collected: dict[str, ToolMessage] = {}
            while i < len(messages):
                cur = messages[i]
                if not isinstance(cur, ToolMessage):
                    break
                tid = getattr(cur, "tool_call_id", None)
                if tid and tid in required:
                    collected[tid] = cur
                i += 1
            for tid in required:
                if tid in collected:
                    out.append(collected[tid])
                else:
                    out.append(
                        ToolMessage(
                            content="[Tool result unavailable in this context.]",
                            tool_call_id=tid,
                            name=name_by_id.get(tid, "tool"),
                        )
                    )
        else:
            out.append(m)
            i += 1
    return out
