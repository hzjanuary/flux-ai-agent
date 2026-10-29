"""Explicit configuration, never loaded at import. JSON profile is private and non-overwriting."""

import json
import os
import re
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from flux.errors import ConfigError
from flux.fs import create_private, no_symlinks, private_dir, private_file
from flux.privacy import Redactor


def placeholder(value: str) -> bool:
    return not value or any(
        s in value.lower() for s in ("your_", "placeholder", "changeme", "example", "xxxx")
    )


@dataclass(frozen=True)
class Settings:
    owner_id: int = 0
    telegram_api_id: int = 0
    telegram_api_hash: str = field(default="", repr=False)
    telegram_bot_token: str = field(default="", repr=False)
    provider_enabled: bool = False
    provider_key: str = field(default="", repr=False)
    model: str = ""
    fallback_models: tuple[str, ...] = ()
    fallback_enabled: bool = False
    max_calls: int = 4
    max_tool_calls: int = 3
    max_output_tokens: int = 512
    timeout: int = 20
    daily_calls: int = 100
    summary_enabled: bool = False
    summary_model: str = ""
    history_limit: int = 20
    web_enabled: bool = False
    web_key: str = field(default="", repr=False)
    system_info_enabled: bool = False
    read_root: str = ""
    notes_preapproved: bool = False
    data_dir: str = ""

    def validate(self, runtime: str = "offline") -> None:
        # Runtime JSON types are checked even when constructing Settings programmatically.
        defaults = Settings()
        for item in fields(self):
            value, default = getattr(self, item.name), getattr(defaults, item.name)
            if type(value) is not type(default):
                raise ConfigError("invalid_config_type")
        for name, maximum in (
            ("max_calls", 16),
            ("max_tool_calls", 8),
            ("max_output_tokens", 4096),
            ("timeout", 120),
            ("daily_calls", 100000),
            ("history_limit", 100),
        ):
            if not 1 <= getattr(self, name) <= maximum:
                raise ConfigError("invalid_resource_limit")
        if not all(
            type(m) is str and re.fullmatch(r"[\w.:-]+/[\w./:-]+", m) for m in self.fallback_models
        ):
            raise ConfigError("invalid_fallback_model")
        if self.read_root:
            if not Path(self.read_root).is_absolute():
                raise ConfigError("absolute_read_root_required")
            no_symlinks(Path(self.read_root))
        if self.data_dir and not Path(self.data_dir).is_absolute():
            raise ConfigError("absolute_data_directory_required")
        if runtime in ("local", "bot"):
            if not self.provider_enabled or placeholder(self.provider_key):
                raise ConfigError("provider_not_configured")
            if placeholder(self.model) or not re.fullmatch(r"[\w.:-]+/[\w./:-]+", self.model):
                raise ConfigError("model_not_configured")
            if self.summary_enabled and (
                placeholder(self.summary_model)
                or not re.fullmatch(r"[\w.:-]+/[\w./:-]+", self.summary_model)
            ):
                raise ConfigError("summary_model_not_configured")
        if runtime == "bot":
            if self.owner_id <= 0:
                raise ConfigError("positive_owner_required")
            if (
                self.telegram_api_id <= 0
                or not re.fullmatch(r"[a-fA-F0-9]{32}", self.telegram_api_hash)
                or placeholder(self.telegram_api_hash)
            ):
                raise ConfigError("telegram_app_not_configured")
            if placeholder(self.telegram_bot_token) or not re.fullmatch(
                r"[1-9]\d{4,}:[A-Za-z0-9_-]{30,}", self.telegram_bot_token
            ):
                raise ConfigError("telegram_bot_not_configured")
        if self.web_enabled and placeholder(self.web_key):
            raise ConfigError("web_not_configured")

    def redactor(self) -> Redactor:
        return Redactor(
            (self.provider_key, self.telegram_api_hash, self.telegram_bot_token, self.web_key)
        )


def default_profile() -> Path:
    return Path.home() / ".config" / "fluxclaw" / "config.json"


def init_profile(path: Path, data_dir: Path | None = None) -> None:
    private_dir(path.parent)
    data = data_dir or Path.home() / ".local" / "share" / "fluxclaw"
    settings = Settings(data_dir=str(data.absolute()))
    create_private(path, (json.dumps(asdict(settings), indent=2) + "\n").encode())


def load(path: Path) -> Settings:
    private_file(path)
    if path.stat().st_size > 32768:
        raise ConfigError("config_too_large")
    raw: dict[str, Any] = json.loads(path.read_text())
    if not isinstance(raw, dict) or set(raw) - {f.name for f in fields(Settings)}:
        raise ConfigError("unknown_config_field")
    if "fallback_models" in raw:
        if not isinstance(raw["fallback_models"], list):
            raise ConfigError("invalid_fallback_model")
        raw["fallback_models"] = tuple(raw["fallback_models"])
    # Explicit process environment overrides; no implicit .env reading.
    env = {
        "TELEGRAM_OWNER_ID": ("owner_id", int),
        "TELEGRAM_API_ID": ("telegram_api_id", int),
        "TELEGRAM_API_HASH": ("telegram_api_hash", str),
        "TELEGRAM_BOT_TOKEN": ("telegram_bot_token", str),
        "OPENROUTER_API_KEY": ("provider_key", str),
        "DEFAULT_MODEL": ("model", str),
    }
    for key, (name, parse) in env.items():
        if key in os.environ:
            raw[name] = parse(os.environ[key])
    result = Settings(**raw)
    result.validate()
    return result
