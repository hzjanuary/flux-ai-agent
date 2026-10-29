# Contributing

Preserve the one-owner Telegram product and reusable bounded Python core. Keep imports/doctor/tests offline; do not introduce public access, implicit models/fallbacks, background provider traffic, EXECUTE or model-driven authorization. Use synthetic fixtures; never read operator .env/session/legacy memory/notes in tests. A regression should exercise a public behavior/boundary, not merely mirror helper implementation.

```bash
uv sync --locked --all-extras
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -q
uv run python scripts/security_gate.py
uv run python scripts/history_audit.py
uv run pip-audit --disable-pip --no-deps -r requirements.lock
```

Tests deny network socket connection/DNS. Provider tests use HTTPX MockTransport, Telegram tests use synthetic events/clients. They are not live evidence. Do not relax defaults for a passing test. Count all routing/fallback/summary attempts within configured budgets; keep successful action receipts durable before acknowledging.

When changing dependencies, update exact pins/uv.lock and regenerate the full production export with `uv export --locked --no-dev --all-extras --no-emit-project --format requirements-txt --output-file requirements.lock`, then run `uv run python scripts/license_inventory.py` and `uv run cyclonedx-py requirements requirements.lock --output-file docs/release/sbom.cdx.json`. Review new licenses and vulnerability results without suppressing unexplained findings. Runtime and dev tooling are separate dependencies; CI audits both.

Changes to filesystem, identity, approvals, persistence or providers require security regression coverage. Each PR must report exact tested revision, fixture vs live evidence, risks and unmet release gates. Keep [SPEC-001](docs/specs/SPEC-001-safe-selfhosted-fluxclaw.md) and the active plan scope intact. Do not publish source/images, push, tag, deploy or run paid/live smoke as a side effect of contribution work.

Project contributions are MIT, with preserved third-party copyrights/NOTICE and explicit provenance review. Do not import upstream code without its actual compatible license and attribution.
