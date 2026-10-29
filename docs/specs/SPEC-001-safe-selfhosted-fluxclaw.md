# SPEC-001 - Safe Self-Hosted FluxClaw Telegram Agent

Status: PROPOSED - not implemented or accepted
Repository: https://github.com/hzjanuary/flux-ai-agent
Observed default-branch baseline: `0eb150a8b5cca3db96bb62f5462a82a25d2ccba1` (2026-10-28 inspection)
Proposed branch: `feat/spec-001-oss-fluxclaw`
Initial scope: single-owner local/personal Telegram agent; not a public multi-user service.

## 1. Outcome

Refactor FluxClaw into an open-source, self-hostable, **secure-by-default personal AI agent** with a reusable, offline-testable agent core and a thin Telegram adapter. Preserve the ReAct conversation loop, smart routing, tool registry and local memory as product differentiators. Do not turn FluxClaw into a duplicate of MAOS; no mandatory LangGraph, Redis, cloud backend or web dashboard.

A new owner should be able to clone and initialize private settings, validate the local core/CLI with no Telegram credentials, explicitly provision a Telegram bot and model provider, confirm a single allowed Telegram user, interact with safe built-in tools, and restart without losing acknowledged memory. Actions which modify files or reach external services must be controlled and traceable.

## 2. Observed baseline and risks (static inspection, not executed)

- `bot.py` allows everyone when `TELEGRAM_OWNER_ID=0`, explicitly called PUBLIC mode, and logs a warning rather than refusing startup. Telegram identity gating must fail closed.
- `tools.py` `run_shell_command()` accepts string prefixes like `ls`/`git diff` and executes through `asyncio.create_subprocess_shell`; prefix checks cannot prevent shell metacharacters or flags. `read_file()` accepts absolute or relative caller-chosen paths without an allowlisted root. `calculate()` uses Python `eval` with restricted globals, which is unnecessary risk in an agent tool.
- `tools.py` directly registers tools and exposes arguments/results to logs. Model-produced JSON tool calls are parsed from text in `brain.py`; there is no centralized capability policy, strict typed schema, confirmation boundary or per-tool resource limit.
- `memory.py` stores per-chat data in one `fluxclaw_memory.json`; it performs read-modify-write JSON persistence and background LLM summaries. This does not provide atomic multi-task writes or guaranteed summary success/retention. Summarization itself consumes provider requests.
- `brain.py` does an ordered OpenRouter fallback on error-string matching, and reports memory/tool usage. Models/defaults may be dated. Tool results are fed back as untrusted text; no hard requirement that the user approve side effects.
- `config.py` creates a singleton at module import and requires Telegram/OpenRouter environment immediately, making offline tests/config inspection less convenient. `.env.example` contains `TELEGRAM_OWNER_ID=0`, sample model IDs and fallback defaults.
- The reviewed tree has no LICENSE file, Dockerfile, Compose, dedicated tests or CI. README says MIT; confirm source ownership and add a valid license before claiming MIT distributability. Note the design influences of other agent projects without importing copyrighted code or assuming their licenses transfer.

Read actual current local source before editing and reconcile any changes after the observed SHA.

## 3. Core product choices

### Keep
- Telegram Bot adapter via Telethon (bot-token mode); real identity verification, bilingual replies and useful `/help`, `/status`, `/reset` commands.
- Configurable legitimate model provider(s), bounded ReAct loop and direct-answer / web path as optional optimizations.
- Persistent per-user memory, with explicit owner control and clear deletion semantics.
- Safe tools: current time, arithmetic, owner-approved notes and an opt-in web search tool.

### Change
- No public mode by default. Missing owner ID, bot credentials or provider credentials must never grant broader authority or silently select paid models.
- Tool registry must validate arguments, classify capabilities (`READ_ONLY`, `NETWORK`, `WRITE`, `EXECUTE`), enforce allowlists and obtain explicit owner approval before any side effect. Shell execution not part of safe default.
- Use a small Python package/core that can be imported/tested without Telethon or remote inference. Telegram is an adapter, not a hard dependency for core tests.
- Versioned, transactional local persistence with isolation and export/reset; model summarization is optional and counted against budgets.

### Out of initial release scope
- Public bots, group-wide autonomous execution, multi-user quotas/billing, arbitrary shell automation, browser/computer control, unattended external file modification, persistent secrets in chat transcripts, claims of guaranteed autonomous task completion.

## 4. Target architecture

```text
Private config (0600) -> CLI init/doctor/tool-list/memory-status
                                  |
Telegram Bot adapter -> Identity/authorization gate -> Agent core
                                                 |       |
                                          bounded LLM   tool policy
                                          + ReAct       + approval
                                                 |       |
                                              SQLite   isolated notes/
                                             per chat  bounded read paths
                                              memory
```

**No Telegram login or provider access during imports, config validation, unit tests, startup health, or security scanning.** Any network calls are tied to an explicit runtime action.

### Identity, access and Telegram transport
- Require positive explicit `TELEGRAM_OWNER_ID`, reject `0` and missing values. Support exactly one owner for the first source preview. Do not enable public/groups by default. If group handling is enabled later, bind both sender identity and allowlisted chat identity; forwarding, bot messages and duplicate updates must not bypass ACL.
- Never send an unauthorized user's message to the model or tools, and do not persist it as owner memory. Ensure commands `/start`, `/help`, `/status`, `/reset` and all non-command events use the same guard.
- Use the existing bot-token flow and avoid requiring userbot/phone credentials. Restrict session files and logs (0700/0600); do not print tokens or identifiers unnecessarily. Handle Telegram message-length limits and eventual retries without duplicate side effects.

### Config, provider and budget
- `flux config init` securely creates a private operator profile, `flux doctor` validates configuration without inference, `flux local chat` tests the isolated core through an explicit provider only when authorized, `flux bot start` starts Telegram.
- Offline unit/integration tests must use injected deterministic test doubles only in tests, never a fake selectable production provider. Real provider adapter checks are separate from actual generation.
- Pin model IDs only as operator configuration; reject missing/unsupported models explicitly. No implicit paid model/fallback; classify HTTP 429/5xx/timeouts, auth/403/billing and invalid output. Fallback requires explicit opt-in, per-turn attempt limit and provider privacy/cost awareness.
- Budget all model calls including **memory summarization**, ReAct loops, routing and retries. Expose max calls/turn, max tokens/output, timeout and optional daily ceiling. Unknown billing remains unknown, not zero. No provider traffic during quickstart until requested.

### Tool capability safety
- Default enabled safe read-only tools: clock and bounded, AST-parsed numeric arithmetic. Validate input size, operator/function whitelist, depth and output magnitude. No Python `eval`.
- `get_system_info`: opt-in; redact hostname/user/IP/home paths and environment details by default.
- `search_web`: opt-in NETWORK capability; outbound query disclosed, bounded result count/time, protect against content prompt injection and untrusted URLs; no automatic fetching arbitrary web URLs.
- `write_note`: WRITE capability requiring explicit owner confirmation or a configurable preapproved notes-only policy. Store strictly beneath private `notes/`, use atomic write, reject traversal/collisions, bound size and log an action receipt without full note content.
- `read_file`: disabled until owner configures an allowlisted read-only root. Resolve paths and symlinks safely; block config, token, session, `.env`, private memory, key and other sensitive paths; limit bytes/encoding. No absolute arbitrary filesystem access.
- `run_shell_command`: **disabled or removed** in v0.1 by default. If explicitly retained as an experimental extension, run argv-only (`shell=False`), executable+argument allowlists with bounded cwd/env/timeout/output; no arbitrary pipes/redirection, `cat` on arbitrary files or shell string prefix matching. No autonomous EXECUTE capability until a separate owner/security decision.
- Typed tool-call protocol enforces name/schema, maximum calls, permission check, side-effect idempotency and audit receipt. The LLM's text is never authority to bypass tool policy. Reject malformed calls without executing partial actions.

### Memory integrity and privacy
- Single-instance default SQLite WAL (or equally robust transactional local store with evidence), keyed by authorized chat ID. No overwriting a single shared JSON blob on concurrent turns; append messages transactionally and preserve ordering.
- If legacy `fluxclaw_memory.json` exists, offer explicit local backup + one-time import preview. Never auto-import, publish or delete it. If import is canceled, preserve source data unchanged.
- Add retention controls and owner-visible `memory list/export/reset --confirm`; `/reset` clears both STM and LTM after explicit scope confirmation, and does not clear another chat.
- Async summary jobs must have durable decision semantics: summary commits only after success; if provider fails, retain source messages and do not truncate unsummarized older half. Count summary calls against budget and allow disabling them entirely.
- Default logs avoid prompt content, memory summaries, Telegram IDs, tool arguments and private file paths. An explicit opt-in debug mode must redact secrets.

### Runtime distribution
- Support Linux/Python on a normal CPU; no GPU required. Optional minimal Docker Compose service uses a read-only root filesystem where feasible, non-root user, cap drop, no-new-privileges, restricted mounts, private data volume and no published HTTP ports. Clearly document Telegram/provider outbound network requirement.
- Use locked dependency versions, a minimal image with project LICENSE/NOTICE and actual third-party license inventory, SBOM, vulnerability reports, CI/security tests, and exact source/image provenance. Do not auto-publish images.
- README includes a Quick Start, local CLI path, Telegram setup, configuration of allowed ID, tool permissions, privacy warning, provider costs/terms, and limitations of self-hosting with remote inference.

## 5. Milestones

**F0 - Preserve and audit:** inspect Git history/secret exposure, fix license provenance, snapshot actual behavior without exposing user memory, write threat model and baseline contracts.

**F1 - Fail-closed identity and isolated core:** move side effects out of module import; typed settings, explicit owner bootstrap, core/Telegram adapter split, secure private configuration and CLI doctor.

**F2 - Harden tools and prompts:** remove dangerous shell/eval defaults, allowlisted filesystem, tool schema/policy/approval, bounded calls, prompt-injection tests, identity routing tests.

**F3 - Durable memory and provider controls:** transactional per-chat storage, legacy migration, safe summarization and concurrency, budget accounting, real adapter error handling and privacy-safe telemetry.

**F4 - Source-release engineering:** regression suite, minimal Docker option, install/backup/restore, CI, docs/licensing/security notice and distinct source-vs-image publication gates.

## 6. Acceptance matrix

| ID | Required evidence |
| --- | --- |
| FLUX-01 | Core package imports and offline CLI doctor work without Telegram/OpenRouter keys or calls. |
| FLUX-02 | Bot startup rejects `TELEGRAM_OWNER_ID=0`, missing owner and placeholder bot/provider config. |
| FLUX-03 | Unauthorized chat/user/command updates never invoke model/tools or touch owner memory. |
| FLUX-04 | Authorized bot receives an actual Telegram text response in a separately permitted live smoke (LIVE; otherwise BLOCKED). |
| FLUX-05 | Duplicate Telegram update does not repeat acknowledged WRITE side effects. |
| FLUX-06 | ReAct loop is bounded and validates structured tool-call schema and arguments. |
| FLUX-07 | Tool registry enforces READ_ONLY/NETWORK/WRITE/EXECUTE capabilities across all call paths. |
| FLUX-08 | Shell injection through command prefixes, operators and metacharacters is impossible by default. |
| FLUX-09 | Arbitrary absolute paths, symlink escapes and secret/session files cannot be read by agent tools. |
| FLUX-10 | Arithmetic is AST-validated and bounded, never Python eval. |
| FLUX-11 | Note writes require authorization, stay in private root and survive restart atomically. |
| FLUX-12 | Web search is opt-in, bounded, clearly treated as lower-trust content. |
| FLUX-13 | Memory is per-authorized-chat transactional and survives abrupt restart without truncated/cross-chat data. |
| FLUX-14 | Failed memory-summary LLM call never discards source messages. |
| FLUX-15 | Memory import/export/reset are explicit, scoped, auditable and preserve original legacy data. |
| FLUX-16 | All ReAct/fallback/summarization model calls counted within turn and daily configured ceilings. |
| FLUX-17 | Auth/billing/permission errors stop without implicit model fallback. |
| FLUX-18 | No provider/model configured => explicit failure, no fake successful answer. |
| FLUX-19 | Logs, traces, errors, Telegram replies and release artifacts have no credential/raw private memory leakage by default. |
| FLUX-20 | Locked dependencies, config/private-path scanner, CI, security test suite and license/source/image gates pass. |
| FLUX-21 | Clean local setup, safe Docker container startup, persistent-volume restart, CLI and owner bot setup documented/tested. |
| FLUX-22 | Source ownership reviewed; actual MIT LICENSE/NOTICE and upstream third-party acknowledgments included. |
| FLUX-23 | Release README and SECURITY.md accurately distinguish personal use, provider privacy/cost and internet-facing risk. |
| FLUX-24 | Live evidence, source publication decision, remote CI and image-security signoff are reported separately. |

Use PASS/FAIL/BLOCKED/NOT_RUN with source SHA, exact test evidence, provider generation count and image identity. Simulated Telegram and injected model fixtures cannot satisfy the optional live criterion. Never weaken default authorization to get green tests.

## 7. Delivery artifacts and release policy

Deliver `README.md`, `docs/architecture.md`, `docs/tool-policy.md`, `docs/security-model.md`, `docs/memory-and-migration.md`, `docs/providers-and-costs.md`, `docs/self-hosting.md`, `docs/release/verification.md`, `docs/release/RELEASE-CHECKLIST.md`, `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, `NOTICE`, safe `.env.example`, real offline CLI/tests, Dockerfile/Compose optional profile, locked dependencies and verified source archive.

Do not automatically deploy Telegram bot, send messages, create paid provider traffic, enable billing, push, merge, tag, publish, rewrite history or delete legacy owner data. If tests cannot safely exercise Telegram, preserve a BLOCKED live criterion and report steps requiring operator participation.
