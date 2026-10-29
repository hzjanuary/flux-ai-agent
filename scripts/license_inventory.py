"""Inventory exact installed production licenses, including PEP 639 metadata."""

import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
locked = dict(
    re.findall(r"^([a-zA-Z0-9-]+)==([^\s;\\]+)", (root / "requirements.lock").read_text(), re.M)
)
raw = subprocess.check_output(
    [
        sys.executable,
        "-m",
        "piplicenses",
        "--packages",
        *locked,
        "--with-authors",
        "--with-urls",
        "--with-license-file",
        "--no-license-path",
        "--with-notice-file",
        "--format=json",
    ],
    text=True,
)
rows = json.loads(raw)
for row in rows:
    distribution = importlib.metadata.distribution(row["Name"])
    expression = distribution.metadata.get("License-Expression")
    if expression:
        row["License"] = expression
    if row["License"] == "UNKNOWN" or row.get("LicenseText") in (None, "UNKNOWN"):
        raise SystemExit("Missing license evidence: " + row["Name"])
(root / "docs/release/third-party-licenses.json").write_text(json.dumps(rows, indent=2) + "\n")
print(f"License texts verified for {len(rows)} production distributions")
