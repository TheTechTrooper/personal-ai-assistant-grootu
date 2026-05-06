import subprocess
from dataclasses import dataclass
from datetime import datetime
import re
import shutil
import os
from pathlib import Path
import socket
import time
import shlex
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
    tool_name: str | None = None
    tool_args: dict | None = None


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
OPENCLAW_BROWSER_PROFILE = os.getenv("OPENCLAW_BROWSER_PROFILE", "openclaw").strip() or "openclaw"


def _openclaw_available() -> bool:
    return _resolve_openclaw_cmd() is not None


def _resolve_openclaw_cmd() -> str | None:
    resolved = shutil.which("openclaw")
    if resolved:
        return resolved

    appdata = os.getenv("APPDATA")
    if appdata:
        candidate = Path(appdata) / "npm" / "openclaw.cmd"
        if candidate.exists():
            return str(candidate)

    return None


def _openclaw_env() -> dict[str, str]:
    env = os.environ.copy()
    path_items = [env.get("PATH", "")]

    appdata = os.getenv("APPDATA")
    if appdata:
        npm_bin = str(Path(appdata) / "npm")
        path_items.insert(0, npm_bin)

    nodejs_dir = r"C:\Program Files\nodejs"
    if Path(nodejs_dir).exists():
        path_items.insert(0, nodejs_dir)

    env["PATH"] = ";".join([item for item in path_items if item])
    return env


def _openclaw_gateway_up(host: str = "127.0.0.1", port: int = 18789) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _ensure_openclaw_gateway() -> bool:
    if _openclaw_gateway_up():
        return True

    cmd = _resolve_openclaw_cmd()
    if not cmd:
        return False

    # Start gateway in user mode (foreground process detached from assistant).
    flags = 0
    if os.name == "nt":
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    try:
        subprocess.Popen(
            [cmd, "gateway", "run"],
            env=_openclaw_env(),
            creationflags=flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False

    for _ in range(10):
        if _openclaw_gateway_up():
            return True
        time.sleep(0.4)
    return False


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
    cmd = _resolve_openclaw_cmd()
    if not cmd:
        return "OpenClaw CLI is not installed. Install it first, then try again."
    if not _ensure_openclaw_gateway():
        return "OpenClaw gateway is not running. Start it with: openclaw gateway run"
    try:
        subprocess.run(
            [cmd, "browser", "start", "--browser-profile", OPENCLAW_BROWSER_PROFILE],
            check=False,
            timeout=30,
            env=_openclaw_env(),
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [cmd, "browser", "open", url, "--browser-profile", OPENCLAW_BROWSER_PROFILE],
            check=True,
            timeout=30,
            env=_openclaw_env(),
        )
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


def _run_openclaw_cli(args: list[str], timeout: int = 45) -> str:
    cmd = _resolve_openclaw_cmd()
    if not cmd:
        return "OpenClaw CLI is not installed. Install it first, then try again."
    if not _ensure_openclaw_gateway():
        return "OpenClaw gateway is not running. Start it with: openclaw gateway run"

    try:
        result = subprocess.run(
            [cmd, *args, "--browser-profile", OPENCLAW_BROWSER_PROFILE]
            if args and args[0] == "browser" and "--browser-profile" not in args
            else [cmd, *args],
            check=False,
            timeout=timeout,
            env=_openclaw_env(),
            capture_output=True,
            text=True,
        )
        output = (result.stdout or "").strip() or (result.stderr or "").strip()
        if result.returncode == 0:
            return output or "OpenClaw command completed."
        return f"OpenClaw command failed: {output or 'unknown error'}"
    except subprocess.TimeoutExpired:
        return "OpenClaw command timed out."
    except Exception:
        return "I could not run that OpenClaw command."


def _start_openclaw_browser() -> str:
    cmd = _resolve_openclaw_cmd()
    if not cmd:
        return "OpenClaw CLI is not installed. Install it first, then try again."
    if not _ensure_openclaw_gateway():
        return "OpenClaw gateway is not running. Start it with: openclaw gateway run"
    try:
        subprocess.run(
            [cmd, "browser", "start", "--browser-profile", OPENCLAW_BROWSER_PROFILE],
            check=True,
            timeout=30,
            env=_openclaw_env(),
        )
        return f"OpenClaw browser is starting (profile: {OPENCLAW_BROWSER_PROFILE})."
    except subprocess.TimeoutExpired:
        return "OpenClaw took too long to start."
    except Exception:
        return "I could not start the OpenClaw browser."


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
        return CommandResult(True, _open_vscode(), tool_name="open_vscode", tool_args={})

    browser_start_phrases = [
        "open chrome",
        "open browser",
        "start browser",
        "open openclaw",
        "open openclaw interface",
        "start openclaw",
    ]
    if any(phrase in normalized for phrase in browser_start_phrases):
        return CommandResult(
            True,
            _start_openclaw_browser(),
            tool_name="openclaw.browser.start",
            tool_args={"browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("open website "):
        target = text[len("open website ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: open website youtube.com")
        return CommandResult(
            True,
            _open_in_openclaw(url),
            tool_name="openclaw.browser.open",
            tool_args={"url": url, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("open site "):
        target = text[len("open site ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: open site github.com")
        return CommandResult(
            True,
            _open_in_openclaw(url),
            tool_name="openclaw.browser.open",
            tool_args={"url": url, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("go to "):
        target = text[len("go to ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid website, for example: go to openai.com")
        return CommandResult(
            True,
            _open_in_openclaw(url),
            tool_name="openclaw.browser.open",
            tool_args={"url": url, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("open "):
        target = text[len("open ") :].strip()
        url = _normalize_url(target)
        if url:
            return CommandResult(
                True,
                _open_in_openclaw(url),
                tool_name="openclaw.browser.open",
                tool_args={"url": url, "browser_profile": OPENCLAW_BROWSER_PROFILE},
            )

    if normalized.startswith("search web for "):
        query = text[len("search web for ") :].strip()
        return CommandResult(
            True,
            _search_web_in_openclaw(query),
            tool_name="openclaw.browser.search",
            tool_args={"query": query, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("search for "):
        query = text[len("search for ") :].strip()
        return CommandResult(
            True,
            _search_web_in_openclaw(query),
            tool_name="openclaw.browser.search",
            tool_args={"query": query, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("google "):
        query = text[len("google ") :].strip()
        return CommandResult(
            True,
            _search_web_in_openclaw(query),
            tool_name="openclaw.browser.search",
            tool_args={"query": query, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("search "):
        query = text[len("search ") :].strip()
        return CommandResult(
            True,
            _search_web_in_openclaw(query),
            tool_name="openclaw.browser.search",
            tool_args={"query": query, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if "show browser tabs" in normalized or normalized == "show tabs":
        return CommandResult(
            True,
            _run_openclaw_cli(["browser", "tabs"]),
            tool_name="openclaw.browser.tabs",
            tool_args={"browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("navigate to "):
        target = text[len("navigate to ") :].strip()
        url = _normalize_url(target)
        if not url:
            return CommandResult(True, "Please provide a valid URL, for example: navigate to openai.com")
        return CommandResult(
            True,
            _run_openclaw_cli(["browser", "navigate", url]),
            tool_name="openclaw.browser.navigate",
            tool_args={"url": url, "browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if "take browser screenshot" in normalized or "take screenshot" in normalized:
        return CommandResult(
            True,
            _run_openclaw_cli(["browser", "screenshot"]),
            tool_name="openclaw.browser.screenshot",
            tool_args={"browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if "browser snapshot" in normalized or "page snapshot" in normalized:
        return CommandResult(
            True,
            _run_openclaw_cli(["browser", "snapshot"]),
            tool_name="openclaw.browser.snapshot",
            tool_args={"browser_profile": OPENCLAW_BROWSER_PROFILE},
        )

    if normalized.startswith("openclaw "):
        raw = text[len("openclaw ") :].strip()
        if not raw:
            return CommandResult(True, "Please provide an OpenClaw command, for example: openclaw browser tabs")
        try:
            args = shlex.split(raw)
        except Exception:
            args = raw.split()
        return CommandResult(True, _run_openclaw_cli(args), tool_name="openclaw.raw", tool_args={"args": args})

    if (
        "show today git commits" in normalized
        or "show todays git commits" in normalized
        or "show git commits today" in normalized
        or "today git commits" in normalized
    ):
        return CommandResult(True, _run_git_today_commits(), tool_name="git.today_commits", tool_args={})

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
            "google",
            "navigate",
            "tab",
            "browser",
            "openclaw",
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
