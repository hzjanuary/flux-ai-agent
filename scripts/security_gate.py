"""Fail-closed source/path/license gate. Reports categories and paths, never matched secrets."""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    rb"sk-or-v1-[a-f0-9]{32,}",
    rb"\b[0-9]{7,}:[A-Za-z0-9_-]{30,}",
    rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
    rb"(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}",
    rb"AKIA[0-9A-Z]{16}",
]
REQUIRED = [
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".env.example",
    "uv.lock",
    "requirements.lock",
    "Dockerfile",
    "compose.yaml",
    "docs/architecture.md",
    "docs/tool-policy.md",
    "docs/security-model.md",
    "docs/memory-and-migration.md",
    "docs/providers-and-costs.md",
    "docs/self-hosting.md",
    "docs/release/verification.md",
    "docs/release/RELEASE-CHECKLIST.md",
    "docs/release/third-party-licenses.json",
    "docs/release/sbom.cdx.json",
]


def paths() -> list[Path]:
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
        )
        .decode()
        .split("\0")
    )
    return sorted({Path(name) for name in names if name})


def scan(data: bytes) -> bool:
    return any(re.search(pattern, data) for pattern in PATTERNS)


def main() -> int:
    failures: list[dict[str, str]] = []
    files = paths()
    for relative in files:
        path = ROOT / relative
        if path.is_symlink():
            failures.append({"path": str(relative), "category": "symlink_in_source"})
            continue
        private = any(
            part in ("notes", ".venv", "__pycache__")
            or (part.startswith(".env") and part != ".env.example")
            or ".session" in part
            or part == "fluxclaw_memory.json"
            or part.endswith((".sqlite3", ".db", ".pem", ".key"))
            for part in relative.parts
        )
        if private:
            failures.append({"path": str(relative), "category": "private_path"})
        if not path.is_file():
            failures.append({"path": str(relative), "category": "missing_source"})
            continue
        data = path.read_bytes()
        if scan(data):
            failures.append({"path": str(relative), "category": "credential_pattern"})
        if relative.parts[0] == "flux" and path.suffix == ".py":
            tree = ast.parse(data)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = (
                        node.func.id
                        if isinstance(node.func, ast.Name)
                        else node.func.attr
                        if isinstance(node.func, ast.Attribute)
                        else ""
                    )
                    if (
                        name
                        in (
                            "eval",
                            "exec",
                            "create_subprocess_shell",
                            "popen",
                            "Popen",
                        )
                        or (
                            isinstance(node.func, ast.Attribute)
                            and isinstance(node.func.value, ast.Name)
                            and node.func.value.id == "os"
                            and name == "system"
                        )
                        or any(k.arg == "shell" for k in node.keywords)
                    ):
                        failures.append({"path": str(relative), "category": "execution_primitive"})
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            failures.append({"path": name, "category": "required_artifact_missing"})
    if (ROOT / "docs/release/third-party-licenses.json").exists():
        licenses = json.loads((ROOT / "docs/release/third-party-licenses.json").read_text())
        locked = re.findall(r"^([a-zA-Z0-9-]+)==", (ROOT / "requirements.lock").read_text(), re.M)

        def canonical(name):
            return re.sub(r"[-_.]+", "-", name).lower()

        indexed = {canonical(row["Name"]): row for row in licenses}
        for name in locked:
            row = indexed.get(canonical(name))
            if (
                row is None
                or row.get("License") in (None, "UNKNOWN")
                or row.get("LicenseText") in (None, "UNKNOWN")
            ):
                failures.append({"path": name, "category": "license_inventory_incomplete"})
    print(json.dumps({"files_scanned": len(files), "failures": failures}, indent=2))
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
