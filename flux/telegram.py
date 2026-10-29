"""One transport-neutral dispatcher and one thin, lazily imported Telethon adapter."""

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path

from flux.config import Settings
from flux.core import Agent
from flux.errors import FluxError
from flux.fs import no_symlinks, private_dir, private_file
from flux.memory import Store
from flux.tools import Registry


@dataclass(frozen=True)
class Update:
    sender: int
    chat: int
    id: int
    text: str
    private: bool = True
    bot: bool = False
    forwarded: bool = False
    outgoing: bool = False


def authorized(settings: Settings, event: Update) -> bool:
    return (
        settings.owner_id > 0
        and event.sender == settings.owner_id
        and event.chat == settings.owner_id
        and event.private
        and not event.bot
        and not event.forwarded
        and not event.outgoing
        and event.id > 0
    )


class Dispatcher:
    def __init__(self, settings: Settings, store: Store, agent: Agent, tools: Registry):
        self.settings, self.store, self.agent, self.tools = settings, store, agent, tools
        self.lock = asyncio.Lock()

    async def handle(self, event: Update) -> str | None:
        # Every command, approval and regular message shares this exact gate.
        if not authorized(self.settings, event):
            return None
        if not event.text.strip() or len(event.text) > 8000:
            return None
        if self.lock.locked():
            return "Đang xử lý / Busy. Please retry after this turn."
        async with self.lock:
            if not self.store.claim(event.chat, event.id):
                return None  # No repeated calls, writes or replies after replay/restart.
            try:
                async with asyncio.timeout(
                    self.settings.timeout
                    * (self.settings.max_calls + self.settings.max_tool_calls + 1)
                ):
                    reply = await self._dispatch(event)
            except FluxError as exc:
                # Exception text can contain upstream data: report only static public codes/types.
                from flux.errors import BudgetExceeded, Denied, InvalidCall, ProviderError

                code = "request_failed"
                if isinstance(exc, ProviderError):
                    code = exc.code
                elif isinstance(exc, BudgetExceeded):
                    code = "budget_exhausted"
                elif isinstance(exc, Denied):
                    code = "action_denied"
                elif isinstance(exc, InvalidCall):
                    code = "invalid_request_or_model_output"
                reply = f"Không hoàn tất / Not completed: {code}."
            except Exception:
                reply = "Không hoàn tất / Not completed: internal_error. Check local doctor."
            reply = self.settings.redactor()(reply)
            self.store.finish(event.chat, event.id, reply)
            return reply

    async def _dispatch(self, event: Update) -> str:
        text = event.text.strip()
        parts = text.split()
        if text.startswith("/"):
            command = parts[0]
            if command in ("/start", "/help") and len(parts) == 1:
                return (
                    "FluxClaw — trợ lý cá nhân / personal assistant.\n/help /status /status latency /reset /approve TOKEN\nTools: "
                    + self.tools.manifest()
                )
            if command == "/status" and parts in (["/status"], ["/status", "latency"]):
                return json.dumps(
                    self.agent.metrics if len(parts) == 2 else self.store.stats(event.chat)
                )
            if parts == ["/reset"]:
                return "Xóa STM + LTM chat này / Clear this chat's messages + summary: /reset confirm. Notes and dedup receipts are kept."
            if parts == ["/reset", "confirm"]:
                self.store.reset(event.chat)
                return "Đã xóa STM + LTM / Messages and summary cleared for this chat."
            if command == "/approve" and len(parts) == 2:
                return await self.tools.approve(event.chat, parts[1])
            return "Lệnh không hợp lệ / Unknown command. Use /help."
        return await self.agent.turn(event.chat, text, str(event.id))


def chunks(text: str) -> list[str]:
    # Telegram limit is UTF-16 code units, not Python code points. Keep headroom.
    result, current, units = [], "", 0
    for char in text:
        size = len(char.encode("utf-16-le")) // 2
        if units + size > 3500:
            result.append(current)
            current, units = "", 0
        current += char
        units += size
    if current:
        result.append(current)
    return result


async def start(settings: Settings, store: Store, dispatcher: Dispatcher) -> None:
    settings.validate("bot")  # Refuse before Telethon import/client/session/network.
    from telethon import TelegramClient, events

    root = private_dir(Path(settings.data_dir))
    session = no_symlinks(root / "telegram.session")
    if session.exists():
        private_file(session)
    os.umask(0o077)
    # Never enable Telethon/HTTP debug logging of transport state or credentials.
    client = TelegramClient(
        str(session),
        settings.telegram_api_id,
        settings.telegram_api_hash,
        request_retries=1,
        connection_retries=1,
        auto_reconnect=True,
    )

    async def on_message(event: object) -> None:  # Telethon is dynamically typed.
        from typing import Any, cast

        item = cast(Any, event)
        update = Update(
            item.sender_id or 0,
            item.chat_id or 0,
            item.id,
            item.raw_text or "",
            bool(item.is_private),
            forwarded=bool(item.message.fwd_from),
            outgoing=bool(item.out),
        )
        if not authorized(settings, update):
            return
        sender = await item.get_sender()
        if not sender or getattr(sender, "bot", True):
            return
        reply = await dispatcher.handle(update)
        if reply is not None:
            for chunk in chunks(reply):
                # Plain text avoids model-controlled formatting/entities/preview fetches.
                await item.reply(chunk, parse_mode=None, link_preview=False)

    client.add_event_handler(on_message, events.NewMessage(incoming=True))
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.sign_in(bot_token=settings.telegram_bot_token)
        me = await client.get_me()
        if not me or not me.bot or me.id != int(settings.telegram_bot_token.split(":", 1)[0]):
            raise FluxError("session_identity_mismatch")
        await client.run_until_disconnected()
    finally:
        await client.disconnect()
