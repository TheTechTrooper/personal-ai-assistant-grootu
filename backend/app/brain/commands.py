import subprocess
from dataclasses import dataclass
from datetime import datetime
import re
import shutil
from urllib.parse import quote_plus

from app.brain.memory import (
    add_note,
    add_task,
    cleanup_memory,
    complete_task,
    get_memory_stats,
    get_profile,
    list_tasks,
    search_notes,
    upsert_profile,
)


@dataclass
class CommandResult:
    handled: bool
    response: str = ""


def _format_tasks(tasks: list[dict]) -> str:
    if not tasks:
        return "You have no pending tasks."
    lines = [f"{task['id']}. {task['description']}" for task in tasks]
    return "Pending tasks:\n" + "\n".join(lines)


def _run_git_today_commits() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--since=midnight", "--pretty=format:%h %s"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
    except Exception:
        return "I could not run git right now."

    if result.returncode != 0:
        return "I could not read git commits for this folder."

    output = result.stdout.strip()
    if not output:
        today = datetime.now().strftime("%Y-%m-%d")
        return f"No commits found for today ({today})."
    return "Today's commits:\n" + output


def _open_vscode() -> str:
    try:
        subprocess.Popen(["code"])
        return "Opening VS Code."
    except Exception:
        return "I could not open VS Code. Please confirm the `code` command is available."


COMMON_SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
    "x": "https://x.com",
    "twitter": "https://x.com",
}


def _openclaw_available() -> bool:
    return shutil.which("openclaw") is not None


def _normalize_url(value: str) -> str:
    candidate = value.strip().lower().strip(" .")
    if not candidate:
        return ""
    if candidate in COMMON_SITES:
        return COMMON_SITES[candidate]
    if not candidate.startswith(("http://", "https://")):
        if "." in candidate:
            return f"https://{candidate}"
        return ""
    return candidate


def _open_in_openclaw(url: str) -> str:
    if not _openclaw_available():
        return "OpenClaw CLI is not installed. Install it first, then try again."
    try:
        subprocess.run(["openclaw", "browser", "open", url], check=True, timeout=30)
        return f"Opening {url} in OpenClaw browser."
    except subprocess.TimeoutExpired:
        return "OpenClaw took too long to respond."
    except Exception:
        return "I could not open that page in OpenClaw."


def _search_web_in_openclaw(query: str) -> str:
    query = query.strip()
    if not query:
        return "Please tell me what to search for."
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    return _open_in_openclaw(search_url)


def handle_command(user_text: str) -> CommandResult:
    text = user_text.strip()
    lower_text = text.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", lower_text)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if lower_text.startswith("remember this:") or normalized.startswith("remember this"):
        if ":" in text:
            note = text.split(":", 1)[1].strip()
        else:
            note = text[len("remember this") :].strip(" .")
        if not note:
            return CommandResult(True, "Please tell me what to remember.")
        note_id = add_note(note)
        return CommandResult(True, f"Saved. Note #{note_id}.")

    if normalized.startswith("my name is"):
        name = text[10:].strip()
        if not name:
            return CommandResult(True, "Please tell me your name.")
        upsert_profile("name", name)
        return CommandResult(True, f"Noted. I will remember your name as {name}.")

    if "what is my name" in lower_text:
        name = get_profile("name")
        if not name:
            return CommandResult(True, "I do not know your name yet.")
        return CommandResult(True, f"Your name is {name}.")

    if normalized.startswith("add task"):
        task = text[8:].strip(" :")
        if not task:
            return CommandResult(True, "Please provide a task description.")
        task_id = add_task(task)
        return CommandResult(True, f"Task added as #{task_id}.")

    if "show pending tasks" in lower_text or "list tasks" in lower_text:
        tasks = list_tasks(status="pending")
        return CommandResult(True, _format_tasks(tasks))

    if normalized.startswith("complete task"):
        tail = normalized.replace("complete task", "", 1).strip()
        if not tail.isdigit():
            return CommandResult(True, "Please provide the task id, for example: complete task 3")
        if complete_task(int(tail)):
            return CommandResult(True, f"Task #{tail} marked as done.")
        return CommandResult(True, f"I could not find a pending task with id #{tail}.")

    if normalized.startswith("what do you know about"):
        query = text[22:].strip(" ?")
        if not query:
            return CommandResult(True, "Please tell me what topic to look up.")
        notes = search_notes(query, limit=5)
        if not notes:
            return CommandResult(True, f"I do not have saved notes about '{query}'.")
        lines = [f"- {note['content']}" for note in notes]
        return CommandResult(True, "Here is what I know:\n" + "\n".join(lines))

    vscode_phrases = [
        "open vscode",
        "open vs code",
        "open visual studio code",
        "launch vscode",
        "launch visual studio code",
        "start vscode",
        "start visual studio code",
    ]
    if any(phrase in normalized for phrase in vscode_phrases):
        return CommandResult(True, _open_vscode())

    if normalized.startswith("open website "):
        target = text[len("open website ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: open website youtube.com")
        return CommandResult(True, _open_in_openclaw(url))

    if normalized.startswith("open site "):
        target = text[len("open site ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: open site github.com")
        return CommandResult(True, _open_in_openclaw(url))

    if normalized.startswith("go to "):
        target = text[len("go to ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: go to openai.com")
        return CommandResult(True, _open_in_openclaw(url))

    if normalized.startswith("open "):
        target = text[len("open ") :].strip()
        url = _normalize_url(target)
        if url:
            return CommandResult(True, _open_in_openclaw(url))

    if normalized.startswith("search web for "):
        query = text[len("search web for ") :].strip()
        return CommandResult(True, _search_web_in_openclaw(query))

    if normalized.startswith("search for "):
        query = text[len("search for ") :].strip()
        return CommandResult(True, _search_web_in_openclaw(query))

    if (
        "show today git commits" in normalized
        or "show todays git commits" in normalized
        or "show git commits today" in normalized
        or "today git commits" in normalized
    ):
        return CommandResult(True, _run_git_today_commits())

    if "memory stats" in normalized or "show memory stats" in normalized:
        stats = get_memory_stats()
        return CommandResult(
            True,
            (
                f"DB: {stats['db_path']}\n"
                f"Notes: {stats['notes_count']} / {stats['max_notes']}\n"
                f"Tasks: {stats['tasks_count']} / {stats['max_tasks']}\n"
                f"Done tasks: {stats['done_tasks_count']} "
                f"(retention: {stats['done_task_retention_days']} days)"
            ),
        )

    if "cleanup memory" in normalized:
        cleanup_memory()
        return CommandResult(True, "Memory cleanup completed.")

    # Prevent command-like voice inputs from falling into long LLM responses.
    command_like = any(
        token in normalized
        for token in [
            "open",
            "show",
            "go to",
            "search",
            "add task",
            "complete task",
            "remember this",
            "my name is",
            "memory",
            "cleanup",
        ]
    )
    if command_like:
        return CommandResult(
            True,
            (
                "I could not match that command. Try: open vscode, open website github.com, "
                "search web for latest AI news, add task ..., show pending tasks, or remember this: ..."
            ),
        )

    return CommandResult(False)
