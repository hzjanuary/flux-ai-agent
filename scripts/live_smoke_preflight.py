"""Offline-only private-input preparation. This script has no live execution entrypoint."""

import argparse
import json
import os
import re
from pathlib import Path

from flux.config import Settings
from flux.fs import create_private, no_symlinks, private_dir, private_file

MODEL = "openai/gpt-oss-20b:free"
RUNTIME_FIELDS = (
    "TELEGRAM_API_ID",
    "TELEGRAM_API_HASH",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_OWNER_ID",
    "OPENROUTER_API_KEY",
    "DEFAULT_MODEL",
)
CONFIRMATIONS = (
    "SMOKE_DEDICATED_TEST_BOT_CONFIRMED",
    "SMOKE_BOT_IDENTITY_CONFIRMED",
    "SMOKE_CREDENTIAL_SCOPE_CONFIRMED",
    "SMOKE_MODEL_ACCESS_CONFIRMED",
    "SMOKE_BILLING_ZERO_SPEND_CONFIRMED",
    "SMOKE_PRIVACY_CONFIRMED",
)
POLICY = {
    "SMOKE_MAX_GENERATION_REQUESTS": "1",
    "SMOKE_MAX_OUTPUT_TOKENS": "128",
    "SMOKE_MAX_SPEND_USD": "0.00",
}
TEMPLATE = {
    "TELEGRAM_API_ID": "",
    "TELEGRAM_API_HASH": "",
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_OWNER_ID": "",
    "OPENROUTER_API_KEY": "",
    "DEFAULT_MODEL": MODEL,
    "SMOKE_EXPECTED_BOT_ID": "",
    "SMOKE_EXPECTED_BOT_USERNAME": "",
    **POLICY,
    **dict.fromkeys(CONFIRMATIONS, "false"),
    "SMOKE_OPERATOR_EVIDENCE_FILE": "",
}


def default_path() -> Path:
    return Path.home() / ".config" / "fluxclaw-live-smoke" / "private.env"


def init_template(path: Path) -> None:
    private_dir(path.parent)
    header = (
        "# Private local inputs only. Never commit, paste, print or source this file.\n"
        "# Native FluxClaw runtime overrides (six fields); the normal CLI does not load .env files.\n"
        "# SMOKE_* fields below are understood ONLY by this offline preflight, not flux.config.\n"
        "# Use literal values, optionally enclosed in matching single/double quotes. No shell expressions.\n"
        "# No retry, fallback, search, summary, tools or background calls are permitted.\n"
        "# A :free model name or true confirmation is not proof of zero billing or model access.\n"
        "# Evidence: private operator record/export of named bot identity, credential scope, model\n"
        "# access/128-token support, zero-spend account controls and reviewed provider privacy.\n"
        "# Leave confirmations false until personally verified. Evidence remains subject to review.\n"
        "# This file cannot grant final live approval; the preflight never connects or infers.\n\n"
    )
    create_private(
        path,
        (header + "\n".join(f"{key}={value}" for key, value in TEMPLATE.items()) + "\n").encode(),
    )


def read_private_env(path: Path) -> dict[str, str]:
    private_file(path)
    info = path.parent.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077 or path.stat().st_nlink != 1:
        raise ValueError("private_input_permissions")
    if path.stat().st_size > 16384:
        raise ValueError("private_input_size")
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or key not in TEMPLATE or key in values:
            raise ValueError("private_input_schema")
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError("private_input_quote")
            value = value[1:-1]
        if "$(" in value or "`" in value or "\x00" in value:
            raise ValueError("private_input_expression")
        values[key] = value
    if set(values) != set(TEMPLATE):
        raise ValueError("private_input_schema")
    return values


def preflight(path: Path) -> dict[str, object]:
    values = read_private_env(path)
    issues: list[str] = []
    for key in (
        *RUNTIME_FIELDS,
        "SMOKE_EXPECTED_BOT_ID",
        "SMOKE_EXPECTED_BOT_USERNAME",
        "SMOKE_OPERATOR_EVIDENCE_FILE",
    ):
        if not values[key]:
            issues.append(key)
    if values["DEFAULT_MODEL"] != MODEL:
        issues.append("DEFAULT_MODEL")
    for key, expected in POLICY.items():
        if values[key] != expected:
            issues.append(key)
    for key in CONFIRMATIONS:
        if values[key] != "true":
            issues.append(key)
    if all(values[key] for key in RUNTIME_FIELDS):
        try:
            settings = Settings(
                owner_id=int(values["TELEGRAM_OWNER_ID"]),
                telegram_api_id=int(values["TELEGRAM_API_ID"]),
                telegram_api_hash=values["TELEGRAM_API_HASH"],
                telegram_bot_token=values["TELEGRAM_BOT_TOKEN"],
                provider_key=values["OPENROUTER_API_KEY"],
                provider_enabled=True,
                model=values["DEFAULT_MODEL"],
                max_calls=1,
                daily_calls=1,
                max_output_tokens=128,
                data_dir=str(path.parent / "campaign-001"),
            )
            settings.validate(
                "bot"
            )  # Structural check only; no provider/client/store instantiated.
            if any(char.isspace() for char in values["OPENROUTER_API_KEY"]):
                issues.append("RUNTIME_CREDENTIAL_FORMAT")
        except Exception:
            issues.append("RUNTIME_CREDENTIAL_FORMAT")
    expected_id = values["SMOKE_EXPECTED_BOT_ID"]
    if expected_id and (
        not re.fullmatch(r"[1-9]\d*", expected_id)
        or values["TELEGRAM_BOT_TOKEN"].split(":", 1)[0] != expected_id
    ):
        issues.append("SMOKE_EXPECTED_BOT_ID")
    username = values["SMOKE_EXPECTED_BOT_USERNAME"].removeprefix("@")
    if username and (
        not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", username)
        or not username.lower().endswith("bot")
    ):
        issues.append("SMOKE_EXPECTED_BOT_USERNAME")
    evidence = values["SMOKE_OPERATOR_EVIDENCE_FILE"]
    if evidence:
        try:
            evidence_path = no_symlinks(Path(evidence).expanduser())
            private_file(evidence_path)
            if evidence_path == path.resolve() or evidence_path.stat().st_size == 0:
                raise ValueError("missing_separate_evidence")
        except Exception:
            issues.append("SMOKE_OPERATOR_EVIDENCE_FILE")
    if (path.parent / "campaign-001").exists():
        issues.append("FRESH_ISOLATED_STORAGE_REQUIRED")
    return {
        "state": "BLOCKED_BEFORE_LIVE",
        "offline_checks": "INCOMPLETE" if issues else "STRUCTURAL_CHECKS_PASS",
        "missing_invalid_or_unconfirmed_fields": sorted(set(issues)),
        "provider": "OpenRouter",
        "exact_model_id": MODEL,
        "maximum_generation_requests": 1,
        "maximum_output_tokens": 128,
        "maximum_spend_usd": "0.00",
        "retry_fallback_search_summary_tools": "FORBIDDEN",
        "credential_and_identity_authentication": "NOT_PERFORMED",
        "billing_model_access_privacy_evidence": "OPERATOR_CLAIMS_ONLY_PENDING_MANUAL_REVIEW",
        "final_operator_confirmation": "REQUIRED_BEFORE_ANY_LIVE_ACCESS",
        "generation_requests": 0,
        "telegram_connections": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=default_path())
    parser.add_argument("--init-template", action="store_true")
    args = parser.parse_args()
    try:
        if args.init_template:
            init_template(args.file)
            print("Private template created; contents withheld. Live remains BLOCKED.")
            return 0
        result = preflight(args.file)
        print(json.dumps(result, indent=2))
        return 0 if result["offline_checks"] == "STRUCTURAL_CHECKS_PASS" else 2
    except Exception:
        print(
            "BLOCKED: private input unavailable, insecure, malformed or already exists; details withheld. Existing content was preserved."
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
