# SPEC-001 verification — local gates pass; release remains blocked

Date: 2026-10-29. Baseline: `0eb150a8b5cca3db96bb62f5462a82a25d2ccba1`. Branch: `feat/spec-001-oss-fluxclaw`. **Plan ACTIVE.** No push, PR, release, image publication, Telegram login, message delivery, model generation or deployment performed.

## Exact scope and identities

- Offline source/test snapshot: `34f0eb53cba518a9e2043d6103d7f5a885c0dbb1`; **203 tests passed**. Final delivery adds evidence/plan documentation only. The final clean HEAD is also retested and archived locally; `artifacts/source-archive.json` records its exact SHA/archive hash without a self-referencing Git commit.
- Local image: `fluxclaw:spec001-verified`; Docker image ID **`sha256:c29173703247edc6318454b0a96f7e88ccae0417dac370ad1016c417144a774e`**. Embedded source revision: **`4d883d93d45dec5765a7499e6db8b75cf7de92f1`**. It is a local OCI image identity, not a published registry digest. All Docker build inputs match the tested source snapshot byte-for-byte: [build-inputs.json](build-inputs.json).
- Python: host clean install/tests 3.13.2; actual container 3.12.16 (Alpine 3.24.3, linux/amd64). GitHub CI targets Python 3.12 but has **not run remotely**.
- **Real provider generations: 0; real summary generations: 0; real Telegram connections/logins/messages: 0; real search requests: 0.** HTTPX transports, model responses and Telethon clients/events in tests are deterministic fixtures. They prove local contracts, not provider availability or actual Telegram delivery.

## Acceptance matrix

PASS here applies to the explicitly stated offline scope. No fixture is treated as LIVE.

| ID | Status | Current evidence / limits |
| --- | --- | --- |
| FLUX-01 | PASS | [clean-install.json](clean-install.json): runtime-only fresh environment has neither Telethon nor OpenAI installed; import/core/doctor/init/tool-list/memory work with socket tripwire and no keys. `test_import_without_keys_or_clients`; isolated first-run subprocess. |
| FLUX-02 | PASS | `test_bot_refuses_before_any_runtime_client` covers zero/negative owner, missing/placeholder bot/app/provider/model; mocked state untouched. Container `bot start` exits 2 under network none. |
| FLUX-03 | PASS | `test_all_unauthorized_paths_have_zero_state_access`: every command/plain text × wrong sender/chat/group/bot/forward/outgoing/invalid update; zero store/model/tool access. Real adapter fixture also rejects before sender lookup. |
| FLUX-04 | BLOCKED | Actual authorized Telegram text response has not been attempted. Requires separate operator permission and private provisioning of bot+provider+owner/model. |
| FLUX-05 | PASS | `test_duplicate_turn_and_write_survive_restart`, processing-claim replay, one-use approval/collision tests; container new-process restart rejects duplicate durable claim. |
| FLUX-06 | PASS | Exact JSON envelope, duplicate/extra/malformed keys rejected; argument schemas; loop/tool/call exhaustion tests. Model requests/output size/timeout enforced. |
| FLUX-07 | PASS | Shared Registry policy; READ_ONLY/NETWORK/WRITE schema and flag tests; model cannot invoke approval or supply approved flags; EXECUTE unconditionally denied and no shell registration. |
| FLUX-08 | PASS | Shell tool absent, injection strings rejected as unknown tool; AST source gate finds no runtime shell/eval/exec primitive. No host shell exploit executed. |
| FLUX-09 | PASS | Traversal/absolute/hidden/secret/config/session/key paths, symlink components, hardlinks, binary/oversize reads blocked through actual registry; descriptor-relative O_NOFOLLOW operations. |
| FLUX-10 | PASS | AST math tests for valid calculations, code/attribute/container/bool/huge-power/nonfinite/depth/length abuse; no eval. |
| FLUX-11 | PASS | Exact-content chat-bound expiring owner approvals; default denies autonomous writes; atomic non-overwriting private notes, restart durability and collision/idempotency tests. |
| FLUX-12 | PASS | Web disabled by default; query disclosed before model/network; one-use owner approval. Actual Brave adapter with HTTP fixture tests bounds, redirects/error/oversize body, untrusted HTTPS sources and redaction; **0 live searches**. |
| FLUX-13 | PASS | Independent concurrent SQLite connections across chats; abrupt process exit during uncommitted write; integrity check/reopen and container process restart. Single runtime OS lock tested. |
| FLUX-14 | PASS | Failed/exhausted/disabled summary preserves source+prior summary; successful summary commits selected unchanged source atomically. No detached/background provider jobs. |
| FLUX-15 | PASS | Synthetic legacy preview, original-byte backup, one-time selected-chat import, export/reset/retention and new-only backup/restore; source unchanged, other chats retained. Real owner data never touched. |
| FLUX-16 | PASS | Shared budget counts direct→ReAct, retries/fallback and summaries; persisted UTC daily reservations tested concurrently and after restart. Unknown billing is explicit. |
| FLUX-17 | PASS | Real HTTP adapter fixtures classify 401/402/403/404 as terminal; no implicit fallback; explicit 429 fallback counts both attempts; transport timeout/error and invalid body tests. |
| FLUX-18 | PASS | No configured/enabled provider/model => CLI/adapter refusal; no selectable fake production model; provider errors never stored as successful assistant answers. |
| FLUX-19 | PASS | Config secrets omitted from repr; redacted prompt/transcript/reply assertions, no prompt/private logging; unexpected SDK exception becomes static CLI failure. Source/history/Trivy secret scans clean. Generic redaction cannot identify every possible secret; backups/imports are intentionally private. |
| FLUX-20 | BLOCKED | Local locks/lint/format/strict types/203 tests, source/history/license/secret gates, production+dev audits and full image scan PASS. Pinned GitHub Actions configured; **remote CI and independent release/security signoff not run/approved**. |
| FLUX-21 | PASS | Fresh runtime-only install, zero-network first-run CLI, actual restricted container initialization/refusal, atomic note+memory persistence over new containers and documented owner provisioning/backup/restore. Actual bot delivery remains FLUX-04 BLOCKED. |
| FLUX-22 | PASS | Full baseline Git authors/history/credits reviewed; same repository owner identities, no vendored upstream source found; LICENSE/NOTICE + 11 exact production license texts. Limits of authorship inference documented; operator publication review remains required. |
| FLUX-23 | PASS | README/SECURITY and operating docs accurately describe personal use, remote inference privacy/cost, plaintext local state, prompt injection, at-most-once uncertain delivery, internet egress and release limitations. |
| FLUX-24 | BLOCKED | Local evidence recorded separately. Live exchange, remote CI, independent image/security signoff and operator source/image publication decisions still pending; no publication performed. |

## Reproduce the local gates

From the repository root, without real credentials:

```bash
uv sync --locked --all-extras
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -q
uv run python scripts/clean_install.py
uv run python scripts/security_gate.py
uv run python scripts/history_audit.py
uv export --locked --all-extras --no-emit-project --format requirements-txt --output-file artifacts/dev-requirements.lock > /dev/null
uv run pip-audit --disable-pip --no-deps -r artifacts/dev-requirements.lock --format json --output artifacts/development-dependency-audit.json
uv run python scripts/source_archive.py
```

Source archive generation requires a clean committed worktree, archives exact HEAD with Git, and checks member types/paths, required artifacts and credential patterns before writing the tar/hash. It does not include `.git`, ignored private files or artifacts. [Earlier candidate archive proof](source-archive-earlier-candidate.json) is explicitly historical; use the generated `artifacts/source-archive.json` for the final delivered docs tree.

Actual image proof:

```bash
docker build --build-arg SOURCE_REVISION="$(git rev-parse HEAD)" -t fluxclaw:local .
uv run python scripts/container_smoke.py fluxclaw:local
```

The host's default Docker build network had a DNS failure; the verified build used `docker build --network host` for dependency downloads only. Every runtime smoke used **--network none**, read-only root, UID 10001, ALL capabilities dropped, no-new-privileges, bounded tmpfs/pids/memory/CPU and a newly created synthetic volume. See [container-proof.json](container-proof.json), [clean-install.json](clean-install.json), [image-contents.json](image-contents.json), [image-scan.json](image-scan.json), [image-gate.json](image-gate.json) and [image SBOM](image-sbom.cdx.json). No existing volume was mounted or removed.

Trivy `0.76` image pinned at `aquasec/trivy@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c`; final full-severity OS+Python+secret scan at 2026-10-29 06:55 UTC: **0 vulnerabilities, 0 secrets**. A fresh exported merged filesystem contains 3717 entries, project LICENSE/NOTICE/license inventory, no Git/private config/session/memory paths. The image SBOM inventories its OS and Python closure. Scans are dated evidence, not a guarantee against future or undetected vulnerabilities; independent image-readiness signoff remains pending.

Initial findings are retained: [Debian image scan](initial-debian-image-scan.json) failed with 44 HIGH findings; [first development audit](initial-development-dependency-audit.json) found vulnerable pytest/lxml; [intermediate Alpine image](intermediate-alpine-image-scan.json) still had 5 MEDIUM + 1 LOW in unused base pip. Development packages were updated; Debian was replaced by the smaller compatible Alpine base; unused pip/ensurepip were removed from the final immutable runtime. No CVE was suppressed/ignored. Current [runtime audit](dependency-audit.json): 11 dependencies, 0 findings; [development audit](development-dependency-audit.json): 69 dependencies, 0 findings. [Production SBOM](sbom.cdx.json) and [license texts](third-party-licenses.json) reflect the locked closure.

History scan used pinned Gitleaks with full reachable history and redaction, plus [history-audit.json](history-audit.json). The eight historical repeated-character Telegram examples were individually classified as synthetic; no confirmed credential was found. Scanners do not prove absence of all secrets. No owner private file was opened or overwritten.

## Remaining authorization and review

Local engineering checks are complete; **source preview is reviewable, not published or accepted as production-ready**. The source/image/CI/live decisions remain separate in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).

Next live permission must explicitly authorize: one named owner/private bot, one explicitly selected model, temporary private credential provisioning, a small maximum generation count and spend ceiling, Telegram login and actual response delivery, plus the desired approval/restart/unauthorized-event smoke. Do not send credentials through chat. Independently authorize any push needed for remote CI. Source release, registry publication/signing and deployment each still require operator review; none follows automatically from a live test.
