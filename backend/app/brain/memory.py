import os
import sqlite3
import threading
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path

_lock = threading.RLock()
_backend_dir = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("ASSISTANT_MEMORY_DB", str(_backend_dir / "assistant_memory.db")))
MAX_NOTES = int(os.getenv("ASSISTANT_MAX_NOTES", "5000"))
MAX_TASKS = int(os.getenv("ASSISTANT_MAX_TASKS", "10000"))
DONE_TASK_RETENTION_DAYS = int(os.getenv("ASSISTANT_DONE_TASK_RETENTION_DAYS", "90"))


class ShortTermMemory:
    def __init__(self, max_messages: int = 20):
        self._messages = deque(maxlen=max_messages)
        self._lock = threading.RLock()

    def add(self, role: str, content: str) -> None:
        with self._lock:
            self._messages.append({"role": role, "content": content.strip()})

    def as_list(self) -> list[dict]:
        with self._lock:
            return list(self._messages)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_memory_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock, _get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);
            CREATE INDEX IF NOT EXISTS idx_tasks_status_updated ON tasks(status, updated_at);
            """
        )


def upsert_profile(key: str, value: str) -> None:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with _lock, _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO profile(key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key.strip().lower(), value.strip(), now),
        )


def get_profile(key: str) -> str | None:
    with _lock, _get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM profile WHERE key = ?",
            (key.strip().lower(),),
        ).fetchone()
        return row["value"] if row else None


def add_note(content: str) -> int:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with _lock, _get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes(content, created_at) VALUES (?, ?)",
            (content.strip(), now),
        )
        note_id = int(cursor.lastrowid)
        _prune_notes(conn)
        return note_id


def search_notes(query: str, limit: int = 5) -> list[dict]:
    pattern = f"%{query.strip()}%"
    with _lock, _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, content, created_at
            FROM notes
            WHERE content LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (pattern, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def add_task(description: str) -> int:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with _lock, _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks(description, status, created_at, updated_at)
            VALUES (?, 'pending', ?, ?)
            """,
            (description.strip(), now, now),
        )
        task_id = int(cursor.lastrowid)
        _prune_tasks(conn)
        return task_id


def list_tasks(status: str = "pending", limit: int = 20) -> list[dict]:
    with _lock, _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, description, status, created_at, updated_at
            FROM tasks
            WHERE status = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def complete_task(task_id: int) -> bool:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with _lock, _get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'done', updated_at = ?
            WHERE id = ? AND status != 'done'
            """,
            (now, task_id),
        )
        _prune_tasks(conn)
        return cursor.rowcount > 0


def _prune_notes(conn: sqlite3.Connection) -> None:
    if MAX_NOTES <= 0:
        return
    conn.execute(
        """
        DELETE FROM notes
        WHERE id NOT IN (
            SELECT id FROM notes ORDER BY id DESC LIMIT ?
        )
        """,
        (MAX_NOTES,),
    )


def _prune_tasks(conn: sqlite3.Connection) -> None:
    if DONE_TASK_RETENTION_DAYS >= 0:
        cutoff = (datetime.utcnow() - timedelta(days=DONE_TASK_RETENTION_DAYS)).isoformat(
            timespec="seconds"
        )
        conn.execute(
            """
            DELETE FROM tasks
            WHERE status = 'done' AND updated_at < ?
            """,
            (cutoff,),
        )

    if MAX_TASKS <= 0:
        return

    conn.execute(
        """
        DELETE FROM tasks
        WHERE id NOT IN (
            SELECT id FROM tasks ORDER BY id DESC LIMIT ?
        )
        """,
        (MAX_TASKS,),
    )


def cleanup_memory() -> None:
    with _lock, _get_connection() as conn:
        _prune_notes(conn)
        _prune_tasks(conn)
    with _lock:
        vacuum_conn = sqlite3.connect(DB_PATH, isolation_level=None)
        try:
            vacuum_conn.execute("VACUUM")
        finally:
            vacuum_conn.close()


def get_memory_stats() -> dict:
    with _lock, _get_connection() as conn:
        notes_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        tasks_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done_tasks_count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'done'"
        ).fetchone()[0]
    return {
        "db_path": str(DB_PATH),
        "notes_count": int(notes_count),
        "tasks_count": int(tasks_count),
        "done_tasks_count": int(done_tasks_count),
        "max_notes": MAX_NOTES,
        "max_tasks": MAX_TASKS,
        "done_task_retention_days": DONE_TASK_RETENTION_DAYS,
    }


def get_relevant_memory(query: str) -> str:
    query_l = (query or "").lower()
    notes = search_notes(query, limit=3)
    name = get_profile("name")
    task_keywords = {
        "task",
        "todo",
        "to do",
        "roadmap",
        "plan",
        "pending",
        "complete",
        "finish",
    }
    include_tasks = any(k in query_l for k in task_keywords)
    tasks = list_tasks(status="pending", limit=5) if include_tasks else []

    parts = []
    if name:
        parts.append(f"Known user name: {name}")
    if notes:
        note_lines = [f"- ({n['id']}) {n['content']}" for n in notes]
        parts.append("Relevant notes:\n" + "\n".join(note_lines))
    if tasks:
        task_lines = [f"- ({t['id']}) {t['description']}" for t in tasks]
        parts.append("Pending tasks:\n" + "\n".join(task_lines))

    return "\n\n".join(parts)


init_memory_db()

