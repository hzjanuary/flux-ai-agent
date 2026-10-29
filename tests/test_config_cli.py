import importlib
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pytest

from flux.config import init_profile, load
from flux.errors import ConfigError, Denied
from flux.provider import OpenRouter
from flux.telegram import start


def configured(settings):
    # Synthetic syntax-valid values; never authenticate them.
    return replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-only-key",
        telegram_api_id=12345,
        telegram_api_hash="0123456789abcdef" * 2,
        telegram_bot_token="123456:" + "Aa1_-B" * 6,
    )


@pytest.mark.parametrize(
    "module",
    [
        "flux",
        "flux.config",
        "flux.core",
        "flux.tools",
        "flux.memory",
        "flux.provider",
        "flux.telegram",
        "brain",
        "tools",
        "config",
        "memory",
        "bot",
    ],
)
def test_import_without_keys_or_clients(module, monkeypatch):
    for key in tuple(os.environ):
        if key.startswith(("TELEGRAM_", "OPENROUTER_", "DEFAULT_MODEL")):
            monkeypatch.delenv(key)
    importlib.reload(importlib.import_module(module))


@pytest.mark.parametrize(
    "overrides",
    [
        {"owner_id": 0},
        {"owner_id": -1},
        {"provider_enabled": False},
        {"provider_key": ""},
        {"provider_key": "your_key_here"},
        {"model": ""},
        {"model": "unsupported-no-vendor"},
        {"telegram_bot_token": ""},
        {"telegram_bot_token": "123456:" + "x" * 32},
        {"telegram_api_hash": "your_hash"},
        {"telegram_api_id": 0},
    ],
)
async def test_bot_refuses_before_any_runtime_client(settings, overrides):
    config = replace(configured(settings), **overrides)
    store, dispatcher = Mock(), Mock()
    with pytest.raises(ConfigError):
        await start(config, store, dispatcher)
    assert not store.mock_calls and not dispatcher.mock_calls


@pytest.mark.parametrize(
    "overrides",
    [
        {"owner_id": True},
        {"max_calls": 0},
        {"max_calls": 1000},
        {"timeout": 0},
        {"max_output_tokens": -1},
        {"fallback_models": (42,)},
        {"notes_preapproved": "true"},
    ],
)
def test_settings_types_and_bounds(settings, overrides):
    with pytest.raises(ConfigError):
        replace(settings, **overrides).validate()


def test_no_production_fake_provider(settings):
    with pytest.raises(ConfigError):
        OpenRouter(settings)


def test_private_init_does_not_overwrite_or_follow_symlink(tmp_path):
    profile = tmp_path / "private" / "config.json"
    init_profile(profile, tmp_path / "data")
    raw = profile.read_bytes()
    assert profile.stat().st_mode & 0o777 == 0o600
    assert profile.parent.stat().st_mode & 0o777 == 0o700
    assert load(profile).provider_enabled is False
    with pytest.raises(FileExistsError):
        init_profile(profile)
    assert profile.read_bytes() == raw
    profile.chmod(0o644)
    with pytest.raises(Denied):
        load(profile)
    alias = tmp_path / "alias"
    alias.symlink_to(profile.parent, target_is_directory=True)
    with pytest.raises(Denied):
        init_profile(alias / "other.json")


def test_clean_first_run_in_subprocess_with_network_tripwire(tmp_path):
    guard = tmp_path / "guard"
    guard.mkdir()
    (guard / "sitecustomize.py").write_text(
        "import socket\ndef deny(*a, **k): raise RuntimeError('network prohibited')\nsocket.socket.connect=deny\nsocket.create_connection=deny\nsocket.getaddrinfo=deny\n"
    )
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("TELEGRAM_", "OPENROUTER_", "DEFAULT_MODEL"))
    }
    env["HOME"] = str(tmp_path / "isolated-home")
    env["PYTHONPATH"] = str(guard) + os.pathsep + str(Path.cwd())
    profile = tmp_path / "profile" / "config.json"
    base = [sys.executable, "-m", "flux", "--config", str(profile)]

    def run(*args):
        return subprocess.run([*base, *args], cwd=tmp_path, env=env, text=True, capture_output=True)

    assert run("doctor").returncode == 0
    assert run("doctor", "--bot").returncode == 2
    assert run("config", "init", "--data-dir", str(tmp_path / "data")).returncode == 0
    assert run("config", "init").returncode == 2
    assert run("doctor").returncode == 0
    assert run("tool-list").returncode == 0
    assert run("memory", "status", "--chat", "42").returncode == 0
    assert run("local", "chat").returncode == 2
    assert run("local", "chat", "--allow-remote").returncode == 2
    assert run("bot", "start").returncode == 2
    assert run("memory", "reset", "--chat", "42").returncode == 2
    assert run("memory", "reset", "--chat", "42", "--confirm").returncode == 0
    assert run("memory", "backup", "--output", str(tmp_path / "backup.sqlite3")).returncode == 0
    assert (
        run(
            "memory",
            "restore",
            "--source",
            str(tmp_path / "backup.sqlite3"),
            "--output",
            str(tmp_path / "restored.sqlite3"),
            "--confirm",
        ).returncode
        == 0
    )
    assert not list(tmp_path.rglob("*.session"))


def test_runtime_failure_never_prints_sdk_payload(monkeypatch, capsys):
    import flux.cli

    monkeypatch.setattr(sys, "argv", ["flux", "doctor"])

    def fail(_):
        raise RuntimeError("sensitive transport payload must not escape")

    monkeypatch.setattr(flux.cli, "run", fail)
    assert flux.cli.main() == 2
    captured = capsys.readouterr()
    assert "sensitive transport" not in captured.err + captured.out
    assert "private details withheld" in captured.err


def test_config_repr_omits_credentials(settings):
    value = replace(
        settings,
        provider_key="secret-synthetic-value",
        telegram_bot_token="secret-synthetic-bot",
        telegram_api_hash="secret-synthetic-hash",
        web_key="secret-synthetic-web",
    )
    assert "secret-synthetic" not in repr(value)
