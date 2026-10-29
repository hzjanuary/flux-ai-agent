import json
from dataclasses import replace
from unittest.mock import Mock

import pytest

from flux.telegram import Dispatcher, Update, chunks


@pytest.mark.parametrize(
    "text",
    [
        "/start",
        "/help",
        "/status",
        "/status latency",
        "/reset",
        "/reset confirm",
        "/approve forged",
        "/unknown",
        "hello",
    ],
)
@pytest.mark.parametrize(
    "changed",
    [
        {"sender": 99},
        {"chat": 99},
        {"private": False},
        {"bot": True},
        {"forwarded": True},
        {"outgoing": True},
        {"id": 0},
    ],
)
async def test_all_unauthorized_paths_have_zero_state_access(settings, text, changed):
    store, agent, tools = Mock(), Mock(), Mock()
    dispatcher = Dispatcher(settings, store, agent, tools)
    assert await dispatcher.handle(replace(Update(42, 42, 1, text), **changed)) is None
    assert not store.mock_calls and not agent.mock_calls and not tools.mock_calls


async def test_owner_zero_is_closed(settings):
    dispatcher = Dispatcher(replace(settings, owner_id=0), Mock(), Mock(), Mock())
    assert await dispatcher.handle(Update(42, 42, 1, "hello")) is None
    assert not dispatcher.store.mock_calls


async def test_commands_do_not_reach_model(build, store):
    dispatcher, model, _, _ = build()
    for index, text in enumerate(
        (
            "/start",
            "/help",
            "/status",
            "/status latency",
            "/reset",
            "/reset confirm",
            "/starter",
            "/statusbogus",
            "/help@other_bot",
            "/unknown",
        ),
        start=1,
    ):
        assert await dispatcher.handle(Update(42, 42, index, text))
    assert not model.calls
    assert store.history(42) == []


async def test_reset_is_explicit_and_scoped(build, store):
    dispatcher, *_ = build()
    store.append(42, "user", "owner")
    store.append(99, "user", "other")
    assert "confirm" in await dispatcher.handle(Update(42, 42, 1, "/reset"))
    assert store.stats(42)["messages"] == 1
    await dispatcher.handle(Update(42, 42, 2, "/reset confirm"))
    assert store.stats(42)["messages"] == 0
    assert store.stats(99)["messages"] == 1


async def test_duplicate_turn_and_write_survive_restart(build, store, settings):
    call = json.dumps(
        {
            "action": "TOOL_CALL",
            "tool_name": "write_note",
            "tool_args": {"title": "todo", "content": "buy milk"},
        }
    )
    dispatcher, model, tools, _ = build(call)
    reply = await dispatcher.handle(Update(42, 42, 1, "save note"))
    token = reply.split()[1]
    assert await dispatcher.handle(Update(42, 42, 1, "save note")) is None
    receipt = await dispatcher.handle(Update(42, 42, 2, f"/approve {token}"))
    assert "Receipt" in receipt
    assert await dispatcher.handle(Update(42, 42, 2, f"/approve {token}")) is None
    assert "action_denied" in await dispatcher.handle(Update(42, 42, 3, f"/approve {token}"))
    from flux.memory import Store

    with_store = Store(store.path)
    dispatcher2 = Dispatcher(settings, with_store, dispatcher.agent, tools)
    try:
        assert await dispatcher2.handle(Update(42, 42, 2, f"/approve {token}")) is None
    finally:
        with_store.close()
    assert len(model.calls) == 1
    assert len(list((store.path.parent / "notes").glob("*.txt"))) == 1


async def test_claimed_unfinished_update_is_never_replayed(build, store):
    store.claim(42, 11)
    dispatcher, model, *_ = build()
    assert await dispatcher.handle(Update(42, 42, 11, "save note")) is None
    assert not model.calls


async def test_busy_does_not_queue_or_touch_state(build, store):
    dispatcher, model, *_ = build()
    async with dispatcher.lock:
        assert "Busy" in await dispatcher.handle(Update(42, 42, 7, "hello"))
    assert not model.calls and not store.history(42)


def test_unicode_telegram_chunks():
    text = "😀" * 6000 + "Việt Nam"
    result = chunks(text)
    assert "".join(result) == text
    assert all(len(c.encode("utf-16-le")) // 2 <= 3500 for c in result)
