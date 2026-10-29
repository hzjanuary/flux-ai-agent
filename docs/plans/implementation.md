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

F0–F4 local engineering implemented and verified: bounded core/CLI, single-owner adapter, approvals/files/math, SQLite migration/recovery, provider budgets/error classes, 235 offline tests, lint/format/strict types, fresh runtime-only install, actual restricted container restart, exact lock/licenses/SBOM/source/history/secret gates and clean full image scan. Detailed per-requirement evidence: docs/release/verification.md.

Plan remains **ACTIVE**. FLUX-04 actual Telegram+provider exchange, FLUX-20 remote CI/independent security-release signoff and FLUX-24 operator publication decisions are BLOCKED by the explicit authorization boundary. No live credentials were requested/used; no push, PR, tag, publication or deployment performed. Do not mark the full goal complete based on local fixtures.

## Follow-up boundary audit (2026-10-29)

Confirmed and fixed private-root exclusion bypass through configured parent components, sensitive root ancestors, and remote response inflation before the byte check. Added pre-body encoding/length checks and bounded identity JSON reads for both real provider/search adapters. Release gates now reject incomplete OS/Python image coverage, missing image identity, stale license versions and stale production exports. Flat Python-only Docker build inputs exclude ignored package data/caches. Ordinary JSON/code answers remain text; reserved tool-call fields still require the strict envelope and cannot grant approval. Quoted credential values are redacted across prompt/transcript/reply boundaries, including whitespace and escapes. 235 offline tests PASS; image rebuilt and rescanned separately. No live/network-runtime permission was inferred from continuation.

## Authorized remote Phase A / private preparation / Phase C

The operator explicitly authorized ordinary feature-branch pushes and exactly one Draft PR into main, then directed completion of Phase A/C after the reviewed export-comment CI failure. Draft PR #1 exists. The fix preserves dependency/version/hash/marker checks; genuine push and PR CI pass at a143673 (252 tests and every gate), with verified downloaded artifacts. FLUX-20 automated gates now PASS; independent review remains FLUX-24 BLOCKED.

Phase B selection: OpenRouter openai/gpt-oss-20b:free, maximum one request, 128 output tokens and 0.00 USD, without retry/fallback/search/summary/tools. A separate private 0600 env template in a 0700 directory and an offline-only preflight were prepared. Bot identity/credentials and billing/access/privacy evidence plus final named confirmation remain pending. No live access is authorized by preflight success. No extra live ACL/recovery/approval tests.

Plan remains ACTIVE. No merge/tag/GitHub release/prebuilt image publication/deployment or independent security signoff is authorized. Source-only v0.1.0 is a review proposal, not an automatic release.

## Owner-authorized early source-only v0.1.0 (2026-10-29)

This newer explicit decision supersedes the historical merge/tag/source-publication holds above for one release only. The owner accepts 22 PASS / 0 FAIL / 2 BLOCKED and authorizes publication documentation, normal push, green final CI, PR #1 ready/merge without bypass, tag v0.1.0 on merged main and one GitHub pre-release with generated source ZIP/tar.gz only. Verify final source/archive/license/private exclusions, release flag/tag/main identities and retain raw evidence. Do not publish a Docker image, connect to Telegram, call a model, search or deploy.

Plan remains **ACTIVE** after source publication: FLUX-04 and FLUX-24 remain BLOCKED until their complete original conditions are satisfied. Live smoke still requires private evidence review and final named operator confirmation. Independent security/image signoff is not fabricated or inferred. Stop after the single source publication; no new implementation, inference or deployment campaign.
