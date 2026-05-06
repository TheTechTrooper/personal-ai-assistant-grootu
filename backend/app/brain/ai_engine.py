from app.brain.commands import handle_command
from app.brain.llm_engine import ask_llm
from app.brain.memory import ShortTermMemory, get_relevant_memory
from dataclasses import dataclass

_short_memory = ShortTermMemory(max_messages=20)
EXIT_WORDS = {"stop", "quit", "exit", "bye", "close"}


@dataclass
class AgentTurn:
    response: str
    route: str  # rule | tool | llm
    tool_name: str | None = None
    tool_args: dict | None = None


def process_input(user_text: str) -> str:
    return process_input_detailed(user_text).response


def process_input_detailed(user_text: str) -> AgentTurn:
    cleaned = (user_text or "").strip()
    if not cleaned:
        return AgentTurn(response="I did not hear anything.", route="rule")

    # Voice input often includes the assistant name prefix.
    if cleaned.lower().startswith("jarvis "):
        cleaned = cleaned[7:].strip()

    lowered = cleaned.lower()
    if lowered in {"hi", "hello", "hey"}:
        return AgentTurn(response="Hello! How can I help you today?", route="rule")

    if lowered in EXIT_WORDS:
        return AgentTurn(response="Okay. I will stop now. Goodbye.", route="rule")

    command = handle_command(cleaned)
    if command.handled:
        _short_memory.add("user", cleaned)
        _short_memory.add("assistant", command.response)
        route = "tool" if command.tool_name else "rule"
        return AgentTurn(
            response=command.response,
            route=route,
            tool_name=command.tool_name,
            tool_args=command.tool_args,
        )

    _short_memory.add("user", cleaned)
    memory_context = get_relevant_memory(cleaned)
    response = ask_llm(
        user_text=cleaned,
        conversation_history=_short_memory.as_list(),
        memory_context=memory_context,
    )
    _short_memory.add("assistant", response)
    return AgentTurn(response=response, route="llm")
