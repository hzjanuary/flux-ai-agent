"""Versioned SQLite WAL storage. All state transitions commit before acknowledgment."""

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from flux.errors import BudgetExceeded, Denied, InvalidCall
from flux.fs import create_private, private_dir, private_file

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, chat INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS summaries(chat INTEGER PRIMARY KEY, content TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS updates(chat INTEGER NOT NULL, update_id INTEGER NOT NULL, state TEXT NOT NULL, reply TEXT NOT NULL DEFAULT '', PRIMARY KEY(chat, update_id));
CREATE TABLE IF NOT EXISTS approvals(token TEXT PRIMARY KEY, chat INTEGER NOT NULL, name TEXT NOT NULL, args TEXT NOT NULL, state TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS receipts(token TEXT PRIMARY KEY, chat INTEGER NOT NULL, name TEXT NOT NULL, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, calls INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS imports(digest TEXT NOT NULL, chat INTEGER NOT NULL, PRIMARY KEY(digest,chat));
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, event TEXT NOT NULL, created REAL NOT NULL);
PRAGMA user_version=1;
"""


class Store:
    def __init__(self, path: Path):
        private_dir(path.parent)
        if not path.exists():
            create_private(path, b"")
        private_file(path)
        self.path = path
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise InvalidCall("unsupported_memory_version")
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def audit(self, event: str) -> None:
        # Only internal constant event names; never include arguments or IDs.
        self.db.execute("INSERT INTO audit(event,created) VALUES(?,?)", (event, time.time()))

    def append(self, chat: int, role: str, content: str) -> None:
        if role not in ("user", "assistant", "tool") or len(content) > 16000:
            raise InvalidCall("invalid_message")
        with self.db:
            self.db.execute(
                "INSERT INTO messages(chat,role,content) VALUES(?,?,?)", (chat, role, content)
            )

    def history(self, chat: int, limit: int = 20) -> list[dict[str, str]]:
        rows = self.db.execute(
            "SELECT role,content FROM (SELECT id,role,content FROM messages WHERE chat=? ORDER BY id DESC LIMIT ?) ORDER BY id",
            (chat, limit),
        )
        return [{"role": row[0], "content": row[1]} for row in rows]

    def summary(self, chat: int) -> str:
        row = self.db.execute("SELECT content FROM summaries WHERE chat=?", (chat,)).fetchone()
        return row[0] if row else ""

    def summary_source(self, chat: int, count: int) -> list[tuple[int, str, str]]:
        return list(
            self.db.execute(
                "SELECT id,role,content FROM messages WHERE chat=? ORDER BY id LIMIT ?",
                (chat, count),
            )
        )

    def commit_summary(self, chat: int, source: list[tuple[int, str, str]], summary: str) -> None:
        if not summary.strip() or not source:
            raise InvalidCall("invalid_summary")
        with self.db:
            current = self.summary_source(chat, len(source))
            if current != source:
                raise Denied("summary_source_changed")
            self.db.execute("INSERT OR REPLACE INTO summaries VALUES(?,?)", (chat, summary))
            self.db.execute("DELETE FROM messages WHERE chat=? AND id<=?", (chat, source[-1][0]))
            self.audit("summary_committed")

    def stats(self, chat: int) -> dict[str, int | bool]:
        return {
            "messages": self.db.execute(
                "SELECT count(*) FROM messages WHERE chat=?", (chat,)
            ).fetchone()[0],
            "has_summary": bool(self.summary(chat)),
        }

    def chats(self) -> list[dict[str, int | bool]]:
        return [
            {"chat": row[0], **self.stats(row[0])}
            for row in self.db.execute("SELECT chat FROM messages UNION SELECT chat FROM summaries")
        ]

    def reset(self, chat: int) -> None:
        with self.db:
            self.db.execute("DELETE FROM messages WHERE chat=?", (chat,))
            self.db.execute("DELETE FROM summaries WHERE chat=?", (chat,))
            self.db.execute("DELETE FROM approvals WHERE chat=?", (chat,))
            # Keep dedup/receipts; reset must not permit replay of acknowledged writes.
            self.audit("memory_reset")

    def retain(self, chat: int, keep: int) -> None:
        if keep < 1:
            raise InvalidCall("invalid_retention")
        with self.db:
            self.db.execute(
                "DELETE FROM messages WHERE chat=? AND id NOT IN (SELECT id FROM messages WHERE chat=? ORDER BY id DESC LIMIT ?)",
                (chat, chat, keep),
            )
            self.audit("explicit_retention")

    def claim(self, chat: int, update_id: int) -> bool:
        with self.db:
            result = self.db.execute(
                "INSERT OR IGNORE INTO updates(chat,update_id,state) VALUES(?,?,'processing')",
                (chat, update_id),
            )
            return result.rowcount == 1

    def finish(self, chat: int, update_id: int, reply: str) -> None:
        with self.db:
            self.db.execute(
                "UPDATE updates SET state='done',reply=? WHERE chat=? AND update_id=?",
                (reply, chat, update_id),
            )

    def reserve_call(self, daily_limit: int) -> None:
        with self.db:
            # BEGIN IMMEDIATE serializes count-and-increment across processes.
            self.db.execute("BEGIN IMMEDIATE")
            day = time.strftime("%Y-%m-%d", time.gmtime())
            row = self.db.execute("SELECT calls FROM usage WHERE day=?", (day,)).fetchone()
            if row and row[0] >= daily_limit:
                raise BudgetExceeded("daily_calls_exhausted")
            self.db.execute(
                "INSERT INTO usage VALUES(?,1) ON CONFLICT(day) DO UPDATE SET calls=calls+1", (day,)
            )

    def request(self, token: str, chat: int, name: str, args: dict[str, Any]) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO approvals VALUES(?,?,?,?,'pending',?)",
                (token, chat, name, json.dumps(args, sort_keys=True), time.time()),
            )
            self.audit("approval_requested")

    def approval(self, token: str, chat: int) -> tuple[str, dict[str, Any], str]:
        row = self.db.execute(
            "SELECT name,args,state,created FROM approvals WHERE token=? AND chat=?", (token, chat)
        ).fetchone()
        if not row or time.time() - row[3] > 600:
            raise Denied("approval_missing_or_expired")
        return row[0], json.loads(row[1]), row[2]

    def consume(self, token: str, chat: int) -> None:
        with self.db:
            result = self.db.execute(
                "UPDATE approvals SET state='consumed' WHERE token=? AND chat=? AND state='pending' AND created>?",
                (token, chat, time.time() - 600),
            )
            if result.rowcount != 1:
                raise Denied("approval_already_consumed")
            self.audit("approval_consumed")

    def receipt(self, token: str, chat: int, name: str) -> None:
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO receipts VALUES(?,?,?,'done')", (token, chat, name)
            )
            self.audit("action_completed")

    def backup(self, destination: Path) -> None:
        private_dir(destination.parent)
        create_private(destination, b"")
        other = sqlite3.connect(destination)
        try:
            self.db.backup(other)
        finally:
            other.close()
        with self.db:
            self.audit("backup_created")

    @staticmethod
    def restore(source: Path, destination: Path) -> None:
        private_file(source)
        # Read-only URI is escaped via as_uri, no caller-provided URI options.
        db = sqlite3.connect(source.absolute().as_uri() + "?mode=ro", uri=True)
        try:
            if (
                db.execute("PRAGMA integrity_check").fetchone()[0] != "ok"
                or db.execute("PRAGMA user_version").fetchone()[0] != 1
            ):
                raise InvalidCall("invalid_backup")
            private_dir(destination.parent)
            create_private(destination, b"")
            target = sqlite3.connect(destination)
            try:
                db.backup(target)
            finally:
                target.close()
        finally:
            db.close()

    def export(self, chat: int, destination: Path) -> None:
        private_dir(destination.parent)
        data = {
            "version": 1,
            "chat": chat,
            "messages": self.history(chat, 1000000),
            "summary": self.summary(chat),
        }
        create_private(destination, json.dumps(data, ensure_ascii=False).encode())
        with self.db:
            self.audit("memory_exported")

    @staticmethod
    def legacy_preview(source: Path, chat: int) -> tuple[str, list[dict[str, str]], str]:
        # Explicit CLI-only read, never reachable from model tools.
        from flux.fs import no_symlinks

        no_symlinks(source)
        if source.stat().st_size > 10_000_000:
            raise InvalidCall("legacy_too_large")
        raw = source.read_bytes()
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get(str(chat)), dict):
            raise InvalidCall("legacy_chat_missing")
        record = data[str(chat)]
        summary = record.get("core_context", "")
        messages = record.get("short_term", [])
        if not isinstance(summary, str) or len(summary) > 16000 or not isinstance(messages, list):
            raise InvalidCall("legacy_invalid")
        for item in messages:
            if (
                not isinstance(item, dict)
                or item.get("role") not in ("user", "assistant", "tool")
                or not isinstance(item.get("content"), str)
                or len(item["content"]) > 16000
            ):
                raise InvalidCall("legacy_invalid")
        return hashlib.sha256(raw).hexdigest(), messages, summary

    def import_legacy(self, source: Path, chat: int, backup: Path) -> None:
        digest, messages, summary = self.legacy_preview(source, chat)
        if self.stats(chat)["messages"] or self.summary(chat):
            raise Denied("import_requires_empty_chat")
        if self.db.execute(
            "SELECT 1 FROM imports WHERE digest=? AND chat=?", (digest, chat)
        ).fetchone():
            raise Denied("already_imported")
        # Back up exact legacy bytes before mutation, preserving source untouched.
        private_dir(backup.parent)
        raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise Denied("legacy_changed")
        create_private(backup, raw)
        with self.db:
            self.db.execute("INSERT INTO imports VALUES(?,?)", (digest, chat))
            self.db.executemany(
                "INSERT INTO messages(chat,role,content) VALUES(?,?,?)",
                [(chat, m["role"], m["content"]) for m in messages],
            )
            self.db.execute("INSERT OR REPLACE INTO summaries VALUES(?,?)", (chat, summary))
            self.audit("legacy_imported")
