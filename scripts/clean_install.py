"""Install runtime-only into a new environment and prove offline CLI without Telethon."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="fluxclaw-clean-") as directory:
    temporary = Path(directory)
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(
            ("TELEGRAM_", "OPENROUTER_", "DEFAULT_MODEL", "UV_PROJECT_ENVIRONMENT", "VIRTUAL_ENV")
        )
    }
    env["UV_PROJECT_ENVIRONMENT"] = str(temporary / "venv")
    subprocess.run(
        ["uv", "sync", "--locked", "--no-dev", "--no-editable"], cwd=root, env=env, check=True
    )
    executable = temporary / "venv" / "bin" / "python"
    code = """
import importlib.util, socket, sys
from pathlib import Path
assert importlib.util.find_spec('telethon') is None
assert importlib.util.find_spec('openai') is None
def deny(*a,**k): raise AssertionError('network prohibited')
socket.socket.connect=deny
socket.create_connection=deny
socket.getaddrinfo=deny
import flux.core, flux.telegram
from flux.cli import main
profile=Path(sys.argv[1])/'profile'/'config.json'
data=Path(sys.argv[1])/'data'
for args in (['doctor'],['config','init','--data-dir',str(data)],['doctor'],['tool-list'],['memory','list']):
 sys.argv=['flux','--config',str(profile),*args]
 assert main()==0
sys.argv=['flux','--config',str(profile),'bot','start']
assert main()==2
print('RUNTIME_ONLY_OFFLINE_PASS')
"""
    completed = subprocess.run(
        [str(executable), "-c", code, str(temporary)],
        cwd=temporary,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    if "RUNTIME_ONLY_OFFLINE_PASS" not in completed.stdout:
        raise RuntimeError("Clean install proof missing")
    proof = {
        "status": "PASS",
        "telegram_installed": False,
        "openai_installed": False,
        "provider_generations": 0,
        "telegram_connections": 0,
        "socket_tripwire": True,
        "commands": [
            "doctor",
            "config init",
            "doctor",
            "tool-list",
            "memory list",
            "bot start refused",
        ],
    }
    (root / "artifacts").mkdir(exist_ok=True)
    (root / "artifacts/clean-install.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))
