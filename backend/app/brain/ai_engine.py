from app.brain.commands import handle_command
from app.brain.llm_engine import ask_llm
from app.brain.memory import ShortTermMemory, get_relevant_memory

_short_memory = ShortTermMemory(max_messages=20)
EXIT_WORDS = {"stop", "quit", "exit", "bye", "close"}


def process_input(user_text: str) -> str:
    cleaned = (user_text or "").strip()
    if not cleaned:
        return "I did not hear anything."

    # Voice input often includes the assistant name prefix.
    if cleaned.lower().startswith("jarvis "):
        cleaned = cleaned[7:].strip()

    lowered = cleaned.lower()
    if lowered in {"hi", "hello", "hey"}:
        return "Hello! How can I help you today?"

    if lowered in EXIT_WORDS:
        return "Okay. I will stop now. Goodbye."

    command = handle_command(cleaned)
    if command.handled:
        _short_memory.add("user", cleaned)
        _short_memory.add("assistant", command.response)
        return command.response

    _short_memory.add("user", cleaned)
    memory_context = get_relevant_memory(cleaned)
    response = ask_llm(
        user_text=cleaned,
        conversation_history=_short_memory.as_list(),
        memory_context=memory_context,
    )
    _short_memory.add("assistant", response)
    return response
