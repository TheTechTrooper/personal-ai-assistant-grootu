import subprocess
import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))


def _build_prompt(
    user_text: str,
    conversation_history: list[dict] | None = None,
    memory_context: str = "",
) -> str:
    history_block = ""
    if conversation_history:
        lines = [
            f"{turn['role'].upper()}: {turn['content']}"
            for turn in conversation_history[-20:]
            if turn.get("content")
        ]
        history_block = "\n".join(lines)

    return (
        "You are Jarvis, a human-like local offline assistant and practical agent.\n"
        "Follow these rules:\n"
        "- Be natural, clear, and friendly.\n"
        "- Keep answers short by default (1-4 sentences), unless user asks for detail.\n"
        "- Do not lecture, moralize, or push unrelated tasks.\n"
        "- If a request is not supported, say it plainly and offer the closest action you can do now.\n"
        "- If the user asks for an action, give an action-first response.\n"
        "- Use saved memory context when relevant.\n"
        "- If you are unsure, say so briefly.\n\n"
        f"MEMORY CONTEXT:\n{memory_context or 'No relevant memory.'}\n\n"
        f"RECENT CONVERSATION:\n{history_block or 'No previous turns.'}\n\n"
        f"USER: {user_text}\n"
        "ASSISTANT:"
    )


def ask_llm(
    user_text: str,
    conversation_history: list[dict] | None = None,
    memory_context: str = "",
) -> str:
    prompt = _build_prompt(user_text, conversation_history, memory_context)
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            return "I could not get a response from Ollama."
        response = result.stdout.strip()
        return response if response else "I do not have a response right now."
    except FileNotFoundError:
        return "Ollama is not installed or not in PATH. Please install Ollama and run `ollama pull mistral:7b`."
    except subprocess.TimeoutExpired:
        return "The model took too long to respond."
    except Exception:
        return "Sorry, my local thinking engine is not available."
