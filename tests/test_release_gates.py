"""A green report must contain actual scan coverage and the current dependency license versions."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("missing", ["os", "os_packages", "python_packages", "identity"])
def test_image_gate_rejects_missing_scan_coverage(tmp_path, missing):
    report = json.loads(Path("docs/release/image-scan.json").read_text())
    if missing == "os":
        report["Results"] = [r for r in report["Results"] if r["Class"] != "os-pkgs"]
    elif missing == "identity":
        report["Metadata"].pop("ImageID", None)
    else:
        category = "os-pkgs" if missing == "os_packages" else "lang-pkgs"
        for result in report["Results"]:
            if result["Class"] == category:
                result["Packages"] = []
    path = tmp_path / "incomplete-report.json"
    path.write_text(json.dumps(report))
    result = subprocess.run(
        [sys.executable, "scripts/image_gate.py", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert '"status": "PASS"' not in result.stdout


def test_current_image_scan_still_has_complete_coverage():
    result = subprocess.run(
        [sys.executable, "scripts/image_gate.py", "docs/release/image-scan.json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0 and '"status": "PASS"' in result.stdout


@pytest.mark.parametrize(
    "changed", [{"Version": "0.0.0"}, {"LicenseText": "UNKNOWN"}, {"License": ""}]
)
def test_license_gate_rejects_stale_or_missing_evidence(changed):
    from scripts.security_gate import license_failures

    row = {
        "Name": "fixture_pkg",
        "Version": "1.2.3",
        "License": "MIT",
        "LicenseText": "synthetic license text",
        **changed,
    }
    assert license_failures([row], "fixture-pkg==1.2.3\n")


def test_current_license_inventory_matches_exact_production_closure():
    from scripts.security_gate import license_failures

    assert not license_failures(
        json.loads(Path("docs/release/third-party-licenses.json").read_text()),
        Path("requirements.lock").read_text(),
    )
