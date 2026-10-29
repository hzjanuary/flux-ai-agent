import sys
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from conftest import ModelFixture

from flux.core import Agent
from flux.errors import FluxError
from flux.telegram import Dispatcher, start
from flux.tools import Registry


async def test_real_adapter_gate_registration_and_plain_reply(settings, store, monkeypatch):
    config = replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-only",
        telegram_api_id=12345,
        telegram_api_hash="0123456789abcdef" * 2,
        telegram_bot_token="123456:" + "Aa1_-B" * 6,
    )
    events = []

    def event(sender=42, chat=42, text="/help", **kwargs):
        result = SimpleNamespace(
            sender_id=sender,
            chat_id=chat,
            id=len(events) + 1,
            raw_text=text,
            is_private=True,
            message=SimpleNamespace(fwd_from=None),
            out=False,
            get_sender=AsyncMock(return_value=SimpleNamespace(bot=False)),
            reply=AsyncMock(),
        )
        for key, value in kwargs.items():
            setattr(result, key, value)
        events.append(result)
        return result

    blocked = [
        event(sender=99),
        event(chat=-99, is_private=False),
        event(message=SimpleNamespace(fwd_from=True)),
        event(out=True),
    ]
    allowed = event()
    bot_sender = event(
        text="should never reach model",
        get_sender=AsyncMock(return_value=SimpleNamespace(bot=True)),
    )

    class Client:
        def __init__(self, *args, **kwargs):
            self.connected = False

        def add_event_handler(self, handler, spec):
            self.handler = handler

        async def connect(self):
            self.connected = True

        async def is_user_authorized(self):
            return False

        async def sign_in(self, *, bot_token):
            assert bot_token == config.telegram_bot_token

        async def get_me(self):
            return SimpleNamespace(bot=True, id=123456)

        async def run_until_disconnected(self):
            for item in events:
                await self.handler(item)

        async def disconnect(self):
            self.connected = False

    monkeypatch.setitem(
        sys.modules,
        "telethon",
        SimpleNamespace(TelegramClient=Client, events=SimpleNamespace(NewMessage=lambda **kw: kw)),
    )
    model = ModelFixture()
    tools = Registry(config, store)
    agent = Agent(config, store, model, tools)
    await start(config, store, Dispatcher(config, store, agent, tools))
    for item in blocked:
        item.get_sender.assert_not_awaited()
        item.reply.assert_not_awaited()
    allowed.reply.assert_awaited_once()
    assert allowed.reply.call_args.kwargs == {"parse_mode": None, "link_preview": False}
    bot_sender.reply.assert_not_awaited()
    assert not model.calls and not store.history(42)


async def test_wrong_existing_session_never_signs_in_or_runs(settings, store, monkeypatch):
    config = replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-only",
        telegram_api_id=12345,
        telegram_api_hash="0123456789abcdef" * 2,
        telegram_bot_token="123456:" + "Aa1_-B" * 6,
    )
    sign_in, run, disconnect = AsyncMock(), AsyncMock(), AsyncMock()
    client = SimpleNamespace(
        add_event_handler=lambda *a: None,
        connect=AsyncMock(),
        is_user_authorized=AsyncMock(return_value=True),
        sign_in=sign_in,
        get_me=AsyncMock(return_value=SimpleNamespace(bot=False, id=999)),
        run_until_disconnected=run,
        disconnect=disconnect,
    )
    monkeypatch.setitem(
        sys.modules,
        "telethon",
        SimpleNamespace(
            TelegramClient=lambda *a, **k: client,
            events=SimpleNamespace(NewMessage=lambda **kw: kw),
        ),
    )
    with pytest.raises(FluxError, match="session_identity_mismatch"):
        await start(config, store, None)
    sign_in.assert_not_awaited()
    run.assert_not_awaited()
    disconnect.assert_awaited_once()
