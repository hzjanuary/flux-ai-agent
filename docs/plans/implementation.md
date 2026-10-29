# SPEC-001 implementation — ACTIVE

Baseline: 0eb150a8b5cca3db96bb62f5462a82a25d2ccba1. Branch: feat/spec-001-oss-fluxclaw.

1. F0: preserve and audit all reachable history, metadata-only private inventory, baseline contracts, ownership and threat review.
2. F1: pure Python core, explicit private config, fail-closed unified Telegram gate and offline CLI.
3. F2: typed capability policy, durable owner approvals, bounded arithmetic, no shell, descriptor-relative file access and atomic notes.
4. F3: transactional per-chat memory, explicit migration/backup/restore, counted opt-in summaries, provider errors/fallback/budgets.
5. F4: deterministic security/integration tests, locked dependencies, lint/types, hardened optional container, CI and source/archive gates.
6. Audit FLUX-01..24 with exact evidence. Keep this plan ACTIVE until separately authorized live smoke, remote CI, release and image review are finished.

No Telegram login, generation, model download, public access, source push or publication authorized. All fixtures use synthetic isolated data. Existing private files and Git history must remain untouched. Small local commits are authorized.

## Local implementation result (2026-10-29)

F0–F4 local engineering implemented and verified: bounded core/CLI, single-owner adapter, approvals/files/math, SQLite migration/recovery, provider budgets/error classes, 232 offline tests, lint/format/strict types, fresh runtime-only install, actual restricted container restart, exact lock/licenses/SBOM/source/history/secret gates and clean full image scan. Detailed per-requirement evidence: docs/release/verification.md.

Plan remains **ACTIVE**. FLUX-04 actual Telegram+provider exchange, FLUX-20 remote CI/independent security-release signoff and FLUX-24 operator publication decisions are BLOCKED by the explicit authorization boundary. No live credentials were requested/used; no push, PR, tag, publication or deployment performed. Do not mark the full goal complete based on local fixtures.

## Follow-up boundary audit (2026-10-29)

Confirmed and fixed private-root exclusion bypass through configured parent components, sensitive root ancestors, and remote response inflation before the byte check. Added pre-body encoding/length checks and bounded identity JSON reads for both real provider/search adapters. Release gates now reject incomplete OS/Python image coverage, missing image identity, stale license versions and stale production exports. Flat Python-only Docker build inputs exclude ignored package data/caches. Ordinary JSON/code answers remain text; reserved tool-call fields still require the strict envelope and cannot grant approval. 232 offline tests PASS; image rebuilt and rescanned separately. No live/network-runtime permission was inferred from continuation.
