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
metadata = report.get("Metadata", {})
os_family = metadata.get("OS", {}).get("Family")
os_coverage = any(
    r.get("Class") == "os-pkgs" and r.get("Type") == os_family and r.get("Packages")
    for r in report.get("Results", [])
)
python_coverage = any(
    r.get("Class") == "lang-pkgs" and r.get("Type") == "python-pkg" and r.get("Packages")
    for r in report.get("Results", [])
)
if (
    not metadata.get("ImageID")
    or report.get("ArtifactType") != "container_image"
    or not os_family
    or not os_coverage
    or not python_coverage
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
