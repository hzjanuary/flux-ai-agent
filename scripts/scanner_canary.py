"""Verify exact-value Gitleaks exceptions still detect a synthetic credential in that file."""

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
output = root / "artifacts"
output.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="fluxclaw-scanner-tripwire-") as directory:
    fixture = Path(directory) / "tests"
    fixture.mkdir()
    # Deliberately not an issued credential. Never use real credentials in scanner tests.
    value = "sk-or-v1-" + hashlib.sha256(b"fluxclaw-synthetic-canary-not-a-real-key").hexdigest()
    (fixture / "test_config_cli.py").write_text('OPENROUTER_API_KEY="' + value + '"\n')
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "-v",
            directory + ":/scan:ro",
            "-v",
            str(root / ".gitleaks.toml") + ":/config.toml:ro",
            "-v",
            str(output) + ":/out",
            "zricethezav/gitleaks@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f",
            "dir",
            "/scan",
            "--config",
            "/config.toml",
            "--redact=100",
            "--no-banner",
            "--report-format",
            "json",
            "--report-path",
            "/out/scanner-canary-redacted.json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    findings = json.loads((output / "scanner-canary-redacted.json").read_text())
    if result.returncode != 1 or not findings:
        raise SystemExit("Credential canary was not detected")
    proof = {
        "status": "PASS",
        "canary": "synthetic OpenRouter-shaped value, not an issued credential",
        "path": "tests/test_config_cli.py",
        "scanner_exit": result.returncode,
        "detected_rules": sorted({f["RuleID"] for f in findings}),
        "allowlists_do_not_disable_other_credentials": True,
    }
    (output / "scanner-canary.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))
