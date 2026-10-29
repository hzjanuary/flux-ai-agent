"""Offline non-root/restart smoke using a newly created synthetic Docker volume only."""

import argparse
import json
import subprocess
import uuid
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("--output", type=Path, default=Path("artifacts/container-proof.json"))
args = parser.parse_args()
volume = "fluxclaw-test-" + uuid.uuid4().hex


def command(argv, expected=0):
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != expected:
        raise RuntimeError(f"Smoke step failed ({result.returncode}): {result.stderr[:1000]}")
    return result.stdout.strip()


command(["docker", "volume", "create", volume])
base = [
    "docker",
    "run",
    "--rm",
    "--network",
    "none",
    "--read-only",
    "--cap-drop",
    "ALL",
    "--security-opt",
    "no-new-privileges",
    "--pids-limit",
    "64",
    "--memory",
    "256m",
    "--cpus",
    "1",
    "--tmpfs",
    "/tmp:rw,noexec,nosuid,size=16m",  # noqa: S108 - isolated container tmpfs, not a host temporary path
    "-v",
    f"{volume}:/data",
]
proof = {}
try:
    metadata = json.loads(command(["docker", "image", "inspect", args.image]))[0]
    if metadata["Config"]["User"] != "10001:10001" or metadata["Config"].get("ExposedPorts"):
        raise RuntimeError("Image user/ports policy failed")
    proof["image_id"] = metadata["Id"]
    proof["source_revision"] = metadata["Config"]["Labels"]["org.opencontainers.image.revision"]
    proof["init"] = command([*base, args.image, "config", "init", "--data-dir", "/data"])
    proof["doctor"] = command([*base, args.image, "doctor"])
    command([*base, args.image, "bot", "start"], expected=2)
    proof["invalid_bot_refused"] = True
    code = """
import asyncio, json, os
from pathlib import Path
from flux.config import Settings
from flux.memory import Store
from flux.tools import Registry
s=Store(Path('/data/memory.sqlite3'))
s.append(42,'user','synthetic durable fixture')
assert s.claim(42,99)
asyncio.run(Registry(Settings(data_dir='/data',notes_preapproved=True),s).execute(42,'write_note',{'title':'fixture','content':'synthetic only'},'stable-action'))
s.close()
try:
 Path('/app/forbidden-write').write_text('no')
 raise AssertionError('root filesystem writable')
except PermissionError: pass
except OSError as e:
 assert e.errno==30
print(json.dumps({'uid':os.getuid(),'profile_mode':oct(Path('/data/config.json').stat().st_mode & 0o777),'data_mode':oct(Path('/data').stat().st_mode & 0o777),'read_only_root':True}))
"""
    proof["write_container"] = json.loads(
        command([*base, "--entrypoint", "python", args.image, "-c", code])
    )
    code2 = """
import json
from pathlib import Path
from flux.memory import Store
s=Store(Path('/data/memory.sqlite3'))
assert len(s.history(42))==1
assert not s.claim(42,99)
notes=list(Path('/data/notes').glob('*.txt'))
assert len(notes)==1 and notes[0].read_text()=='fixture\\nsynthetic only\\n'
assert s.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
print(json.dumps({'memory_survives_restart':True,'note_survives_restart':True,'duplicate_claim_refused':True,'integrity':'ok'}))
s.close()
"""
    proof["restart_container"] = json.loads(
        command([*base, "--entrypoint", "python", args.image, "-c", code2])
    )
    proof.update(
        {
            "network": "none",
            "telegram_connections": 0,
            "provider_generations": 0,
            "status": "PASS",
            "cap_drop": "ALL",
            "no_new_privileges": True,
        }
    )
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))
finally:
    # Exact task-created synthetic volume; never touches operator volumes.
    command(["docker", "volume", "rm", volume])
