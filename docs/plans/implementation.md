# SPEC-001 implementation — ACTIVE

Baseline: 0eb150a8b5cca3db96bb62f5462a82a25d2ccba1. Branch: feat/spec-001-oss-fluxclaw.

1. F0: preserve and audit all reachable history, metadata-only private inventory, baseline contracts, ownership and threat review.
2. F1: pure Python core, explicit private config, fail-closed unified Telegram gate and offline CLI.
3. F2: typed capability policy, durable owner approvals, bounded arithmetic, no shell, descriptor-relative file access and atomic notes.
4. F3: transactional per-chat memory, explicit migration/backup/restore, counted opt-in summaries, provider errors/fallback/budgets.
5. F4: deterministic security/integration tests, locked dependencies, lint/types, hardened optional container, CI and source/archive gates.
6. Audit FLUX-01..24 with exact evidence. Keep this plan ACTIVE until separately authorized live smoke, remote CI, release and image review are finished.

No Telegram login, generation, model download, public access, source push or publication authorized. All fixtures use synthetic isolated data. Existing private files and Git history must remain untouched. Small local commits are authorized.
