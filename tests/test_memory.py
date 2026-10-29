import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from flux.errors import BudgetExceeded, Denied, ProviderError
from flux.memory import Store
from flux.provider import Budget


def test_concurrent_per_chat_appends_survive_restart(store):
    def append(chat):
        connection = Store(store.path)
        try:
            for index in range(30):
                connection.append(chat, "user", f"chat {chat} item {index}")
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(append, [1, 2, 3, 4]))
    second = Store(store.path)
    try:
        for chat in range(1, 5):
            assert second.history(chat, 100) == [
                {"role": "user", "content": f"chat {chat} item {i}"} for i in range(30)
            ]
        assert second.db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        second.close()


def test_abrupt_process_exit_preserves_committed_not_partial(store):
    code = """
import os, sys
from pathlib import Path
from flux.memory import Store
s=Store(Path(sys.argv[1]))
s.append(42,'user','committed')
s.db.execute('BEGIN IMMEDIATE')
s.db.execute("INSERT INTO messages(chat,role,content) VALUES(42,'user','uncommitted')")
os._exit(0)
"""
    subprocess.run([sys.executable, "-c", code, str(store.path)], check=True)
    assert store.history(42) == [{"role": "user", "content": "committed"}]
    assert store.db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


async def test_summary_failure_keeps_all_source_and_old_summary(build, store):
    dispatcher, model, _, agent = build(
        ProviderError("authentication"),
        summary_enabled=True,
        summary_model="operator/summary",
        history_limit=4,
    )
    for _ in range(5):
        store.append(42, "user", "preserve this unsummarized synthetic text")
    with store.db:
        store.db.execute("INSERT INTO summaries VALUES(42,'prior summary')")
    before = store.history(42)
    budget = Budget(store, 4, 100)
    await agent.maybe_summarize(42, budget)
    assert store.history(42) == before
    assert store.summary(42) == "prior summary"
    assert budget.calls == len(model.calls) == 1


async def test_summary_success_commits_atomically_and_counts(build, store):
    _, model, _, agent = build(
        "summary fixture", summary_enabled=True, summary_model="operator/summary", history_limit=4
    )
    for index in range(4):
        store.append(42, "user", str(index))
    budget = Budget(store, 4, 100)
    await agent.maybe_summarize(42, budget)
    assert store.summary(42) == "summary fixture"
    assert [m["content"] for m in store.history(42)] == ["2", "3"]
    assert budget.calls == 1 and model.calls[0]["model"] == "operator/summary"


async def test_disabled_or_exhausted_summary_never_discards(build, store):
    _, model, _, agent = build()
    for _ in range(25):
        store.append(42, "user", "keep")
    await agent.maybe_summarize(42, Budget(store, 1, 100))
    assert len(store.history(42, 100)) == 25 and not model.calls
    _, model2, _, agent2 = build(summary_enabled=True, summary_model="operator/summary")
    await agent2.maybe_summarize(42, Budget(store, 1, 100, calls=1))
    assert len(store.history(42, 100)) == 25 and not model2.calls


def test_legacy_preview_import_backup_export_reset_preserve_original(store, tmp_path):
    source = tmp_path / "legacy.json"
    raw = json.dumps(
        {
            "42": {
                "short_term": [{"role": "user", "content": "legacy synthetic"}],
                "core_context": "old summary",
            },
            "99": {"short_term": [{"role": "user", "content": "other private synthetic"}]},
        }
    ).encode()
    source.write_bytes(raw)
    backup = tmp_path / "backup.json"
    digest, messages, summary = store.legacy_preview(source, 42)
    assert len(digest) == 64 and len(messages) == 1 and summary == "old summary"
    assert not store.history(42) and not backup.exists()
    store.import_legacy(source, 42, backup)
    assert source.read_bytes() == backup.read_bytes() == raw
    assert not store.history(99)
    output = tmp_path / "export.json"
    store.export(42, output)
    assert json.loads(output.read_text())["messages"] == messages
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(Denied):
        store.import_legacy(source, 42, tmp_path / "backup2.json")
    store.reset(42)
    with pytest.raises(Denied):
        store.import_legacy(source, 42, tmp_path / "backup2.json")
    assert source.read_bytes() == raw


def test_backup_restore_new_destination_only(store, tmp_path):
    store.append(42, "user", "durable synthetic")
    backup = tmp_path / "backup.sqlite3"
    restored_path = tmp_path / "restored.sqlite3"
    store.backup(backup)
    Store.restore(backup, restored_path)
    restored = Store(restored_path)
    try:
        assert restored.history(42) == store.history(42)
    finally:
        restored.close()
    with pytest.raises(FileExistsError):
        Store.restore(backup, restored_path)


def test_explicit_retention_is_scoped(store):
    for index in range(8):
        store.append(42, "user", str(index))
    store.append(99, "user", "keep other chat")
    store.retain(42, 3)
    assert [m["content"] for m in store.history(42)] == ["5", "6", "7"]
    assert len(store.history(99)) == 1


def test_daily_reservations_atomic_under_concurrent_connections(store):
    def reserve(_):
        connection = Store(store.path)
        try:
            connection.reserve_call(5)
            return True
        except BudgetExceeded:
            return False
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(reserve, range(12)))
    assert sum(results) == 5
