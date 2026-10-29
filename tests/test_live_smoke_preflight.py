"""Only synthetic private files; no live SDK/client is imported by the preflight."""

import hashlib
import json

import pytest

from flux.errors import Denied
from scripts.live_smoke_preflight import (
    CONFIRMATIONS,
    MODEL,
    init_template,
    main,
    preflight,
    read_private_env,
)


def configured(path):
    init_template(path)
    evidence = path.parent / "operator-record.txt"
    evidence.write_text("synthetic operator evidence; not service authentication")
    evidence.chmod(0o600)
    values = read_private_env(path)
    values.update(
        TELEGRAM_API_ID="12345",
        TELEGRAM_API_HASH=hashlib.sha256(b"synthetic-preflight-app").hexdigest()[:32],
        TELEGRAM_BOT_TOKEN="123456:" + "Aa1_-B" * 6,
        TELEGRAM_OWNER_ID="42",
        OPENROUTER_API_KEY="synthetic-credential-do-not-print",
        SMOKE_EXPECTED_BOT_ID="123456",
        SMOKE_EXPECTED_BOT_USERNAME="fixture_test_bot",
        SMOKE_OPERATOR_EVIDENCE_FILE=str(evidence),
    )
    values.update(dict.fromkeys(CONFIRMATIONS, "true"))
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
    return values


def test_template_is_private_nonoverwriting_and_blocked(tmp_path):
    path = tmp_path / "private" / "private.env"
    init_template(path)
    before = path.read_bytes()
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    with pytest.raises(FileExistsError):
        init_template(path)
    assert path.read_bytes() == before
    result = preflight(path)
    assert result["state"] == "BLOCKED_BEFORE_LIVE" and result["offline_checks"] == "INCOMPLETE"
    assert read_private_env(path)["DEFAULT_MODEL"] == MODEL


def test_valid_synthetic_inputs_still_never_authorize_live(tmp_path, monkeypatch):
    path = tmp_path / "private" / "private.env"
    values = configured(path)
    monkeypatch.setenv("TELEGRAM_OWNER_ID", "999")
    result = preflight(path)
    assert result["offline_checks"] == "STRUCTURAL_CHECKS_PASS"
    assert result["state"] == "BLOCKED_BEFORE_LIVE"
    output = json.dumps(result)
    assert values["OPENROUTER_API_KEY"] not in output and values["TELEGRAM_BOT_TOKEN"] not in output
    assert result["generation_requests"] == result["telegram_connections"] == 0
    assert not (path.parent / "campaign-001").exists()


@pytest.mark.parametrize(
    "changed",
    [
        {"DEFAULT_MODEL": "different/model"},
        {"SMOKE_MAX_GENERATION_REQUESTS": "2"},
        {"SMOKE_MAX_OUTPUT_TOKENS": "129"},
        {"SMOKE_MAX_SPEND_USD": "0.01"},
        {"SMOKE_EXPECTED_BOT_ID": "987654"},
        {"SMOKE_PRIVACY_CONFIRMED": "false"},
    ],
)
def test_policy_drift_and_unconfirmed_claims_block(tmp_path, changed):
    path = tmp_path / "private" / "private.env"
    values = configured(path)
    values.update(changed)
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
    assert preflight(path)["offline_checks"] == "INCOMPLETE"


@pytest.mark.parametrize(
    "suffix",
    ["TELEGRAM_OWNER_ID=99\n", "UNKNOWN=anything\n", "OPENROUTER_API_KEY=$(touch marker)\n"],
)
def test_unknown_duplicate_and_shell_inputs_are_rejected_without_execution(tmp_path, suffix):
    path = tmp_path / "private.env"
    init_template(path)
    path.write_text(path.read_text() + suffix)
    with pytest.raises(ValueError):
        read_private_env(path)
    assert not (tmp_path / "marker").exists()


def test_insecure_or_linked_file_is_rejected(tmp_path):
    path = tmp_path / "private" / "private.env"
    init_template(path)
    path.chmod(0o644)
    with pytest.raises(Denied):
        read_private_env(path)
    path.chmod(0o600)
    alias = path.parent / "alias.env"
    alias.symlink_to(path)
    with pytest.raises(Denied):
        read_private_env(alias)


def test_main_withholds_all_error_values(tmp_path, monkeypatch, capsys):
    path = tmp_path / "private" / "private.env"
    configured(path)
    path.write_text(path.read_text() + "UNRECOGNIZED=synthetic-must-not-print\n")
    monkeypatch.setattr("sys.argv", ["preflight", "--file", str(path)])
    assert main() == 2
    output = capsys.readouterr().out
    assert "synthetic-must-not-print" not in output and "details withheld" in output
