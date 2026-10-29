"""Create and verify a local archive of an exact committed tree; never publish it."""

import argparse
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

from security_gate import REQUIRED, ROOT, scan

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts")
args = parser.parse_args()
if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
    raise SystemExit("Source archive requires a clean committed worktree")
sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
raw = subprocess.check_output(["git", "archive", "--format=tar", sha], cwd=ROOT)
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    names = set()
    for member in archive:
        name = Path(member.name)
        if name.is_absolute() or ".." in name.parts or member.issym() or member.islnk():
            raise SystemExit("Unsafe archive member")
        if any(
            p in ("notes", ".venv", "__pycache__")
            or (p.startswith(".env") and p != ".env.example")
            or ".session" in p
            or p.endswith((".sqlite3", ".db"))
            or p == "fluxclaw_memory.json"
            for p in name.parts
        ):
            raise SystemExit("Private path in archive")
        names.add(str(name))
        if member.isfile():
            stream = archive.extractfile(member)
            if stream is None or scan(stream.read()):
                raise SystemExit("Credential pattern in archive")
    if set(REQUIRED) - names:
        raise SystemExit("Missing required source artifact")
args.output_dir.mkdir(exist_ok=True, parents=True)
path = args.output_dir / f"fluxclaw-{sha}.tar"
path.write_bytes(raw)
proof = {
    "source_sha": sha,
    "archive": path.name,
    "sha256": hashlib.sha256(raw).hexdigest(),
    "members": len(names),
    "private_paths_or_credential_findings": 0,
    "status": "PASS",
}
(args.output_dir / "source-archive.json").write_text(json.dumps(proof, indent=2) + "\n")
print(json.dumps(proof, indent=2))
