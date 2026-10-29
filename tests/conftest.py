import socket
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from flux.config import Settings
from flux.core import Agent
from flux.memory import Store
from flux.telegram import Dispatcher
from flux.tools import Registry


class ModelFixture:
    def __init__(self, *responses: str | Exception):
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    async def complete(self, messages, model, max_tokens, timeout):
        self.calls.append(
            {
                "messages": deepcopy(messages),
                "model": model,
                "max_tokens": max_tokens,
                "timeout": timeout,
            }
        )
        if not self.responses:
            raise AssertionError("Unexpected model call")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Tests must never use a network socket")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)


@pytest.fixture
def settings(tmp_path):
    return Settings(owner_id=42, data_dir=str(tmp_path / "data"), model="operator/model")


@pytest.fixture
def store(settings):
    result = Store(Path(settings.data_dir) / "memory.sqlite3")
    yield result
    result.close()


@pytest.fixture
def build(settings, store):
    def factory(*responses, **overrides):
        config = replace(settings, **overrides)
        model = ModelFixture(*responses)
        tools = Registry(config, store)
        agent = Agent(config, store, model, tools)
        return Dispatcher(config, store, agent, tools), model, tools, agent

    return factory
