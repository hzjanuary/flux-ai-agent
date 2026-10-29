"""Full reachable Git-blob audit, redact all potential matches; never rewrite history."""

import json
import re
import subprocess

from security_gate import PATTERNS, ROOT

objects = subprocess.check_output(
    ["git", "rev-list", "--objects", "--all"], cwd=ROOT, text=True
).splitlines()
findings, examples, count = [], 0, 0
for entry in objects:
    oid, _, name = entry.partition(" ")
    if subprocess.check_output(["git", "cat-file", "-t", oid], cwd=ROOT).strip() != b"blob":
        continue
    count += 1
    data = subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT)
    for pattern in PATTERNS:
        for match in re.finditer(pattern, data):
            # Only the reviewed, repeated-character Telegram example in historical docs.
            value = match[0]
            if (
                name in (".env.example", "README.md")
                and re.fullmatch(rb"\d+:[A-Za-z0-9_-]+", value)
                and len(set(value.split(b":")[1])) <= 3
            ):
                examples += 1
            else:
                findings.append(
                    {"object": oid, "path": name, "category": "REDACTED_candidate_requires_review"}
                )
print(
    json.dumps(
        {
            "objects": len(objects),
            "blobs": count,
            "reviewed_synthetic_examples": examples,
            "findings": findings,
        },
        indent=2,
    )
)
raise SystemExit(bool(findings))
