# FluxClaw - OSS Implementation Roadmap

Planning baseline: main `0eb150a8b5cca3db96bb62f5462a82a25d2ccba1`; SPEC-001 is authoritative. This is a proposal and not evidence of tests or implementation.

## Release posture

- v0.1 source-preview scope: a **single-owner**, private Telegram AI agent with a testable standalone core, safe tool permissions and durable, bounded memory.
- No public bot or autonomous shell execution. No model/Telegram login during offline tests. Only opt-in live connection later.
- MIT cannot be asserted from the existing README alone: a project LICENSE is absent from the reviewed tracked tree and ownership must be confirmed.

| Sequence | Work package | Required output | Exit gate |
| --- | --- | --- | --- |
| F0 | History/security audit | Review prior commits, secrets, LICENSE provenance and attack paths; baseline negative tests | No confirmed private token in candidate, attributions and current risk recorded |
| F1 | Fail-closed owner identity | Typed config, secure init, core/Telegram separation, owner-only guards | `TELEGRAM_OWNER_ID=0` and missing secrets cannot start bot; unauthorized handler tests PASS |
| F2 | Tool sandbox and consent | Schema/capability gate, no shell prefix execution, AST math, bounded roots, note approval | Untrusted tool call, `ls; ...`, symlink and arbitrary file attacks rejected |
| F3 | Reliable privacy and memory | Atomic per-chat state, explicit import/reset, async summarization safety and budget | Concurrent append/restart, failed summary and owner reset tests PASS |
| F4 | Provider contract and local CLI | Bounded ReAct, error classification, request budgets, CLI doctor, optional local chat | No implicit model calls, no success masquerading as failed API output |
| F5 | Source packaging and CI | Lock, minimal optional Docker, tests, secrets gates, licenses, README/SECURITY | FLUX acceptance matrix, actual isolated container/CLI verification and honest live blocker |

## First local actions for Codex

1. Do not open or print the owner's existing `.env`, Telethon `*.session`, `notes/` or `fluxclaw_memory.json`. Inspect filenames/permissions and create isolated test data.
2. Read `bot.py` authorization, `tools.py` shell/file/eval paths, `brain.py` textual tool call/fallback and `memory.py` read-modify-write persistence.
3. Create a minimal failing security regression test for unauthorized messages and the shell prefix + `shell=True` pattern; do **not** run a shell exploit on operator host.
4. Prepare branch, plan, exact per-tool permission matrix and migration strategy before moving existing memory data.

## Evidence policy

- Use synthetic Telegram events, no actual Telegram messages. A real bot exchange is a separate LIVE condition.
- Side-effectful tools require actual policy checks in the shared execution path; a prompt instruction alone is not security.
- Summarizer LLM calls cost budget; do not silently discard messages on failed summarization.
- Keep raw source/image scanner findings and no unreviewed exceptions. Preserve legacy data untouched.
- No source push, Telegram login or hosted inference without explicit owner authorization.
