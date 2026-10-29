# SPEC-001 verification — remote CI passes; live/release remain blocked

Date: 2026-10-29. Baseline: `0eb150a8b5cca3db96bb62f5462a82a25d2ccba1`. Branch: `feat/spec-001-oss-fluxclaw`. **Plan ACTIVE; 22 PASS / 0 FAIL / 2 BLOCKED.** The owner explicitly authorized early source-only v0.1.0 publication through PR #1 despite FLUX-04 and FLUX-24 remaining BLOCKED. Final merge/tag/release outcomes belong to the GitHub release and final operator evidence, not the historical snapshots below. No prebuilt image publication, Telegram connection/login/delivery, model generation or deployment is authorized by this decision.

## Historical local scope and identities

- Offline source/test snapshot: `c4cf3286a8f9fdff145f5bfa8690bc5354b5adca`; **235 tests passed**. The follow-up audit added pre-decoding HTTP limits, canonical private-root checks, ordinary structured-answer routing, quoted credential redaction and fail-closed scan/license coverage gates. The listed image was rebuilt from this exact code snapshot. Final delivery adds evidence/operating documentation; runtime/image build inputs remain unchanged from this snapshot. The final clean HEAD is also retested and archived locally; `artifacts/source-archive.json` records its exact SHA/archive hash without a self-referencing Git commit.
- Local image: `fluxclaw:spec001-review2`; Docker image ID **`sha256:6664713599bd1fc216a545c16990e6646211f74daa28859c9c0aa9a976546d1a`**. Embedded source revision: **`c4cf3286a8f9fdff145f5bfa8690bc5354b5adca`**. It is a local OCI image identity, not a published registry digest. All Docker build inputs match the tested source snapshot byte-for-byte: [build-inputs.json](build-inputs.json).
- Python: host clean install/tests 3.13.2; actual container 3.12.16 (Alpine 3.24.3, linux/amd64). Genuine GitHub CI ran on Python 3.12.15; see the remote evidence below.
- **Real provider generations: 0; real summary generations: 0; real Telegram connections/logins/messages: 0; real search requests: 0.** HTTPX transports, model responses and Telethon clients/events in tests are deterministic fixtures. They prove local contracts, not provider availability or actual Telegram delivery.

## Authorized remote verification

PR: https://github.com/hzjanuary/flux-ai-agent/pull/1 (targeting main). Workflow ID: `400337039`. The last verified source before publication documentation was `0b8dc3405452faff9f4133044d558164a12285f3`: push [40843691774](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40843691774) and PR [40843697225](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40843697225) both passed offline/container jobs with 252 tests. Four downloaded ZIP digests and source bytes/modes were verified. Both image scans on 2026-10-29 08:39 UTC reported zero vulnerabilities and zero secrets. Final publication documentation must pass the same CI before merge; the release notes record those final runs and the merged main SHA.

The following earlier verified snapshot and its raw evidence are preserved: `a143673c534b2c43f4b89c5e04a99622625a884d`.

| Event | Run | Offline | Container |
| --- | --- | --- | --- |
| push | [40842059971](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40842059971) | PASS: 252 tests, lint/types, isolated install, source/history/license/secret/dependency gates and archive | PASS: non-root/restart proof, full scan and SBOM |
| pull_request | [40842064814](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40842064814) | PASS: 252 tests and all source gates | PASS: non-root/restart proof, full scan and SBOM |

All four artifact ZIPs were downloaded, checked against GitHub's SHA-256 digest and CRC/path-validated. Source tar hashes, every tracked file byte and file mode match the source snapshot. PR checkout/image/archive use synthetic merge `7fa09a2d8aae7da69e5524cbea773183d911ef2d`; its tree equals the actual feature head. The push image is `sha256:2f72e271d8b4620e1d7af9d2af54d95bf5b2b38c9eb7c55242b0fdb1609c0f0d`; the PR image is `sha256:361d7c2fa7628fa6ed2fc33b256d08b98e24d4bdb392b4754510e27de30e748d`. Both scans have zero vulnerabilities and zero secrets. Full run/job/artifact/digest/provenance records: [remote-verification.json](remote-verification.json). Original ZIPs, raw scans, SBOMs and job logs are retained locally under `artifacts/remote-verification/runs/<run-id>/` and as GitHub Actions artifacts; these local evidence paths are excluded from source distribution.

Initial genuine runs `40837677218` and `40837832607` failed at `production_lock_export_stale`: local uv 0.6.5 lacked uv 0.9.7's indented `# via` comments. Read-only reproduction established exact equality of every noncomment requirement line, version, hash and marker. The authorized fix ignores indented comments only; regression tests still reject real version/hash/marker changes. The first fixed runs `40841351858` and `40841358463` passed. All earlier failure evidence and the reviewed patch remain preserved; no scanner was disabled and no dependency/hash change was hidden.

Phase B operator selection is OpenRouter `openai/gpt-oss-20b:free`, one request, 128 output tokens, 0.00 USD, no retry/fallback/search/summary/tools. Dedicated bot identity and private credentials/evidence have not been authenticated. A 0600 private template in a 0700 dedicated directory and an offline-only checker are prepared; see [live-smoke-preparation.md](live-smoke-preparation.md). The checker never grants live approval. Real generations/connections/deliveries remain zero.

Automated source/image gate acceptance (FLUX-20) is distinct from independent human security review and full release completion (FLUX-24). The owner authorized **early source-only v0.1.0**; see [source-only-v0.1.0.md](source-only-v0.1.0.md). This limited decision does not clear FLUX-04 or FLUX-24. Final HEAD/run/archive identities are recorded in release notes and local `artifacts/` evidence rather than trying to embed a commit's own SHA inside itself.

## Acceptance matrix

PASS here applies to the explicitly stated offline scope. No fixture is treated as LIVE.

| ID | Status | Current evidence / limits |
| --- | --- | --- |
| FLUX-01 | PASS | [clean-install.json](clean-install.json): runtime-only fresh environment has neither Telethon nor OpenAI installed; import/core/doctor/init/tool-list/memory work with socket tripwire and no keys. `test_import_without_keys_or_clients`; isolated first-run subprocess. |
| FLUX-02 | PASS | `test_bot_refuses_before_any_runtime_client` covers zero/negative owner, missing/placeholder bot/app/provider/model; mocked state untouched. Container `bot start` exits 2 under network none. |
| FLUX-03 | PASS | `test_all_unauthorized_paths_have_zero_state_access`: every command/plain text × wrong sender/chat/group/bot/forward/outgoing/invalid update; zero store/model/tool access. Real adapter fixture also rejects before sender lookup. |
| FLUX-04 | BLOCKED | Selected OpenRouter `openai/gpt-oss-20b:free`, one request/128 output tokens/0.00 USD; dedicated bot username/identity, private credentials, billing/access/privacy evidence and final named live approval are still pending. Zero live requests/connections/deliveries. |
| FLUX-05 | PASS | `test_duplicate_turn_and_write_survive_restart`, processing-claim replay, one-use approval/collision tests; container new-process restart rejects duplicate durable claim. |
| FLUX-06 | PASS | Exact JSON envelope, duplicate/extra/malformed keys rejected; argument schemas; loop/tool/call exhaustion tests. Model requests/output size/timeout enforced. Ordinary JSON/code answers remain text without invoking tools; arrays/code fences purporting to call tools are rejected. |
| FLUX-07 | PASS | Shared Registry policy; READ_ONLY/NETWORK/WRITE schema and flag tests; model cannot invoke approval or supply approved flags; EXECUTE unconditionally denied and no shell registration. |
| FLUX-08 | PASS | Shell tool absent, injection strings rejected as unknown tool; AST source gate finds no runtime shell/eval/exec primitive. No host shell exploit executed. |
| FLUX-09 | PASS | Traversal/absolute/hidden/secret/config/session/key paths, symlink components, hardlinks, binary/oversize reads blocked through actual registry; descriptor-relative O_NOFOLLOW operations. New tests confirm `..` in configured roots cannot expose private storage and sensitive root ancestors cannot hide behind harmless relative filenames. |
| FLUX-10 | PASS | AST math tests for valid calculations, code/attribute/container/bool/huge-power/nonfinite/depth/length abuse; no eval. |
| FLUX-11 | PASS | Exact-content chat-bound expiring owner approvals; default denies autonomous writes; atomic non-overwriting private notes, restart durability and collision/idempotency tests. |
| FLUX-12 | PASS | Web disabled by default; query disclosed before model/network; one-use owner approval. Actual Brave adapter with HTTP fixture tests bounds, redirects/error/oversize body, untrusted HTTPS sources and redaction; **0 live searches**. Compressed/oversized responses are rejected before body reads; undeclared streamed bodies stop at the byte ceiling. |
| FLUX-13 | PASS | Independent concurrent SQLite connections across chats; abrupt process exit during uncommitted write; integrity check/reopen and container process restart. Single runtime OS lock tested. |
| FLUX-14 | PASS | Failed/exhausted/disabled summary preserves source+prior summary; successful summary commits selected unchanged source atomically. No detached/background provider jobs. |
| FLUX-15 | PASS | Synthetic legacy preview, original-byte backup, one-time selected-chat import, export/reset/retention and new-only backup/restore; source unchanged, other chats retained. Real owner data never touched. |
| FLUX-16 | PASS | Shared budget counts direct→ReAct, retries/fallback and summaries; persisted UTC daily reservations tested concurrently and after restart. Unknown billing is explicit. |
| FLUX-17 | PASS | Real HTTP adapter fixtures classify 401/402/403/404 as terminal; no implicit fallback; explicit 429 fallback counts both attempts; transport timeout/error and invalid body tests. |
| FLUX-18 | PASS | No configured/enabled provider/model => CLI/adapter refusal; no selectable fake production model; provider errors never stored as successful assistant answers. |
| FLUX-19 | PASS | Config secrets omitted from repr; redacted prompt/transcript/reply assertions including quoted JSON/Python credential fields, whitespace and escapes, no prompt/private logging; unexpected SDK exception becomes static CLI failure. Source/history/Trivy secret scans clean. Generic redaction cannot identify every possible secret; backups/imports are intentionally private. |
| FLUX-20 | PASS | Genuine push and PR CI on `0b8dc34` (runs 40843691774 / 40843697225), and the earlier `a143673`, passed all jobs, 252 tests, lint/types, isolated install, exact lock/license/source/history/secret/dependency/archive gates and container scan/restart/SBOM. Artifact ZIP digests, source bytes/modes and source/image trees validated. Final publication CI must also pass. This is automated verification, not independent signoff. |
| FLUX-21 | PASS | Fresh runtime-only install, zero-network first-run CLI, actual restricted container initialization/refusal, atomic note+memory persistence over new containers and documented owner provisioning/backup/restore. Actual bot delivery remains FLUX-04 BLOCKED. |
| FLUX-22 | PASS | Full baseline Git authors/history/credits reviewed; same repository owner identities, no vendored upstream source found; LICENSE/NOTICE + 11 exact production license texts. Limits of authorship inference documented; operator publication review remains required. |
| FLUX-23 | PASS | README/SECURITY and operating docs accurately describe personal use, remote inference privacy/cost, plaintext local state, prompt injection, at-most-once uncertain delivery, internet egress and release limitations. |
| FLUX-24 | BLOCKED | Remote CI, source/archive/image provenance, live evidence and publication decisions remain separate. Owner approval covers only an early source-only v0.1.0 preview. Actual Telegram/provider evidence is absent; independent security/ownership review, complete original release conditions and separate image-security signoff remain outstanding. Source publication alone cannot mark this criterion PASS. |

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
uv run python scripts/scanner_canary.py
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

Trivy `0.76` image pinned at `aquasec/trivy@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c`; final full-severity OS+Python+secret scan at 2026-10-29 07:29 UTC: **0 vulnerabilities, 0 secrets**. A fresh exported merged filesystem contains 3719 entries, project LICENSE/NOTICE/license inventory, no Git/private config/session/memory paths. The image SBOM inventories its OS and Python closure. Scans are dated evidence, not a guarantee against future or undetected vulnerabilities; independent image-readiness signoff remains pending.

Initial findings are retained: [Debian image scan](initial-debian-image-scan.json) failed with 44 HIGH findings; [first development audit](initial-development-dependency-audit.json) found vulnerable pytest/lxml; [intermediate Alpine image](intermediate-alpine-image-scan.json) still had 5 MEDIUM + 1 LOW in unused base pip. Development packages were updated; Debian was replaced by the smaller compatible Alpine base; unused pip/ensurepip were removed from the final immutable runtime. No CVE was suppressed/ignored. Current [runtime audit](dependency-audit.json): 11 dependencies, 0 findings; [development audit](development-dependency-audit.json): 69 dependencies, 0 findings. [Production SBOM](sbom.cdx.json) and [license texts](third-party-licenses.json) reflect the locked closure.

History scan used pinned Gitleaks v8.30.1 with full reachable history and redaction, plus [history-audit.json](history-audit.json). The eight historical repeated-character Telegram examples were individually classified as synthetic; no confirmed credential was found. Scanners do not prove absence of all secrets. No owner private file was opened or overwritten. The final default-rule Gitleaks scan flagged nine false positives: three occurrences of the syntax-only `0123456789abcdef` test app hash and six occurrences of the official Python base image’s **public** GPG signing fingerprint. Raw redacted findings are retained in [gitleaks-reviewed-findings.json](gitleaks-reviewed-findings.json). `.gitleaks.toml` extends all defaults and restricts each reviewed exception by exact value AND exact file pattern for only generic-api-key. It does not skip commits, directories or real credential formats. [scanner-canary.json](scanner-canary.json) proves an unrelated synthetic credential is still detected inside an exception-listed file. The configured full-history rescan passes; these are reviewed content classifications, not removed findings or broad exceptions.

## Remaining authorization and review

The owner explicitly accepts a limited early source-only v0.1.0 preview with **22 PASS / 0 FAIL / 2 BLOCKED**, subject to final candidate checks and normal GitHub merge rules. This is not full SPEC-001 completion, production acceptance or independent signoff. The source/image/CI/live decisions remain separate in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).

The model and budget are selected, but Phase B remains BLOCKED. Complete the private input file locally, run the offline preflight and STOP for manual evidence review and final confirmation of the named bot/owner/model/zero-spend conditions before any live access. Do not send credentials or owner IDs through chat. The only proposed live scope is one synthetic private exchange: no extra live ACL, approval or recovery tests are authorized; preserve their offline evidence separately. Normal PR merge, tag v0.1.0 and one source-only GitHub pre-release are now explicitly authorized after final gates; live access, registry publication/signing and deployment remain outside this publication campaign.
