"""Explicit local operations. Only local chat --allow-remote and bot start can infer."""

import argparse
import asyncio
import json
import logging
import os
import secrets
import sys
from pathlib import Path

from flux.config import Settings, default_profile, init_profile, load
from flux.core import Agent
from flux.errors import FluxError
from flux.fs import RuntimeLock
from flux.memory import Store
from flux.provider import OpenRouter
from flux.telegram import Dispatcher, start
from flux.tools import Registry


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="flux")
    root.add_argument("--config", type=Path, default=default_profile())
    subs = root.add_subparsers(dest="command", required=True)
    config = subs.add_parser("config").add_subparsers(dest="config_command", required=True)
    init = config.add_parser("init")
    init.add_argument("--data-dir", type=Path)
    doctor = subs.add_parser("doctor")
    doctor.add_argument("--bot", action="store_true")
    subs.add_parser("tool-list")
    local = (
        subs.add_parser("local")
        .add_subparsers(dest="local_command", required=True)
        .add_parser("chat")
    )
    local.add_argument(
        "--allow-remote",
        action="store_true",
        help="Explicitly permit paid/provider traffic for this session",
    )
    subs.add_parser("bot").add_subparsers(dest="bot_command", required=True).add_parser("start")
    memory = subs.add_parser("memory").add_subparsers(dest="memory_command", required=True)
    memory.add_parser("list")
    for name in ("status", "export", "reset", "retain", "import"):
        p = memory.add_parser(name)
        p.add_argument("--chat", type=int, required=True)
        if name == "export":
            p.add_argument("--output", type=Path, required=True)
        if name in ("reset", "retain", "import"):
            p.add_argument("--confirm", action="store_true")
        if name == "retain":
            p.add_argument("--keep", type=int, required=True)
        if name == "import":
            p.add_argument("--source", type=Path, required=True)
            p.add_argument("--backup", type=Path)
    backup = memory.add_parser("backup")
    backup.add_argument("--output", type=Path, required=True)
    restore = memory.add_parser("restore")
    restore.add_argument("--source", type=Path, required=True)
    restore.add_argument("--output", type=Path, required=True)
    restore.add_argument("--confirm", action="store_true")
    return root


def open_store(settings: Settings) -> Store:
    if not settings.data_dir or not Path(settings.data_dir).is_absolute():
        raise FluxError("absolute_data_directory_required")
    return Store(Path(settings.data_dir) / "memory.sqlite3")


async def local_chat(settings: Settings, store: Store) -> None:
    tools = Registry(settings, store)
    agent = Agent(settings, store, OpenRouter(settings), tools)
    print("Remote provider session; costs unknown. /quit to exit. Local chat uses isolated chat 0.")
    while True:
        text = await asyncio.to_thread(input, "> ")
        if text == "/quit":
            return
        try:
            if text.startswith("/approve "):
                result = await tools.approve(0, text.split(maxsplit=1)[1])
            elif text.startswith("/"):
                result = "Use /approve TOKEN or /quit; memory commands are separate CLI operations."
            else:
                result = await agent.turn(0, text, secrets.token_hex(16))
            print(settings.redactor()(result))
        except Exception:
            print("Request not completed; details withheld. Check doctor and budgets.")


def run(args: argparse.Namespace) -> int:
    if args.command == "config":
        init_profile(args.config, args.data_dir)
        print(
            "Private configuration created; remote inference disabled. Edit it locally, then run flux doctor."
        )
        return 0
    if args.command == "doctor" and not args.config.exists():
        if args.bot:
            print("FAIL: private config missing; bot refused.")
            return 2
        print(
            "Offline core OK; no profile configured; remote inference disabled. Run flux config init."
        )
        return 0
    settings = load(args.config)
    if args.command == "doctor":
        settings.validate("bot" if args.bot else "offline")
        print("PASS: offline configuration valid; generation calls=0; Telegram connections=0.")
        if not args.bot:
            try:
                settings.validate("bot")
                print("Bot configuration structurally ready; no credentials authenticated.")
            except FluxError:
                print("Bot not configured; startup remains disabled.")
        return 0
    if args.command == "local":
        if not args.allow_remote:
            raise FluxError("local_chat_requires_allow_remote")
        settings.validate("local")
    if args.command == "bot":
        settings.validate("bot")
    if args.command == "memory" and args.memory_command == "restore":
        if not args.confirm:
            raise FluxError("restore_requires_confirm")
        Store.restore(args.source, args.output)
        print("Restored to a NEW destination; existing memory not overwritten.")
        return 0
    runtime_lock = RuntimeLock(Path(settings.data_dir))
    store: Store | None = None
    try:
        store = open_store(settings)
        if args.command == "tool-list":
            print(Registry(settings, store).manifest())
        elif args.command == "local":
            asyncio.run(local_chat(settings, store))
        elif args.command == "bot":
            tools = Registry(settings, store)
            agent = Agent(settings, store, OpenRouter(settings), tools)
            asyncio.run(start(settings, store, Dispatcher(settings, store, agent, tools)))
        elif args.command == "memory":
            command = args.memory_command
            if command == "list":
                print(json.dumps(store.chats()))
            elif command == "status":
                print(json.dumps(store.stats(args.chat)))
            elif command == "export":
                store.export(args.chat, args.output)
                print("Private export created; contains conversation data.")
            elif command == "backup":
                store.backup(args.output)
                print("Private database backup created.")
            elif command in ("reset", "retain"):
                if not args.confirm:
                    raise FluxError("memory_change_requires_confirm")
                if command == "reset":
                    store.reset(args.chat)
                else:
                    store.retain(args.chat, args.keep)
                print("Scoped memory operation committed.")
            elif command == "import":
                _, messages, summary = store.legacy_preview(args.source, args.chat)
                print(
                    json.dumps(
                        {
                            "messages": len(messages),
                            "has_summary": bool(summary),
                            "preview_only": not args.confirm,
                        }
                    )
                )
                if args.confirm:
                    if not args.backup:
                        raise FluxError("legacy_backup_required")
                    store.import_legacy(args.source, args.chat, args.backup)
                    print("Imported selected chat once; original source preserved.")
        return 0
    finally:
        if store is not None:
            store.close()
        runtime_lock.close()


def main() -> int:
    os.umask(0o077)
    logging.basicConfig(level=logging.CRITICAL)  # No prompt/raw transport diagnostics.
    args = parser().parse_args()
    try:
        return run(args)
    except (FluxError, OSError, ValueError, TypeError):
        print(
            "FAIL: operation refused or unavailable. Check private configuration, permissions and required confirmations.",
            file=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
