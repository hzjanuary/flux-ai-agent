"""Review full Trivy JSON without hiding lower-severity findings; fail high/critical/secrets."""

import json
import sys
from collections import Counter
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
counts: Counter[str] = Counter()
secrets = 0
for result in report.get("Results", []):
    for vulnerability in result.get("Vulnerabilities", []):
        counts[vulnerability["Severity"]] += 1
    secrets += len(result.get("Secrets", []))
if not report.get("Metadata", {}).get("OS") or not any(
    r.get("Type") == "python-pkg" for r in report.get("Results", [])
):
    raise SystemExit("Incomplete OS/Python image scan")
failed = bool(secrets or counts["HIGH"] or counts["CRITICAL"])
print(
    json.dumps(
        {
            "severity_counts": counts,
            "secrets": secrets,
            "status": "FAIL" if failed else "PASS",
            "artifact": report.get("ArtifactName"),
            "created_at": report.get("CreatedAt"),
        },
        indent=2,
    )
)
raise SystemExit(failed)
