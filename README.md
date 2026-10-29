# FluxClaw

A self-hosted personal Telegram AI agent for one owner, in Vietnamese or English. A small Python ReAct core, smart direct/web/tool routing, typed tools and durable per-chat SQLite memory; Telethon is a thin optional adapter. Python 3.12+, ordinary CPU, no model download or cloud backend required.

This branch is a **source preview under review**. Live Telegram/provider behavior and publication approval are separate gates in [verification](docs/release/verification.md). There is no public-user mode or autonomous shell execution.

## Safe local quick start

Install [uv](https://docs.astral.sh/uv/), then from this checkout:

```bash
uv sync --locked
uv run flux doctor
uv run flux config init
uv run flux doctor
uv run flux tool-list
uv run flux memory list
uv run pytest -q
```

The quick start makes **zero Telegram connections and zero model requests**. Dependency installation downloads Python packages. The private JSON profile defaults to `~/.config/fluxclaw/config.json` (0600); data defaults to `~/.local/share/fluxclaw` (0700). Initialization refuses existing files. Choose isolated paths with `flux --config /absolute/private/config.json config init --data-dir /absolute/private/data`. Commands put `--config` **before** the subcommand. No `.env` is loaded automatically.

The default profile has no credentials/model, `provider_enabled=false`, no fallback, summaries or web search, and `owner_id=0`. Zero means **startup refused**, never public access. `doctor` checks local settings, not credentials against a remote service; use `doctor --bot` for strict startup readiness.

## Provision your private bot explicitly

Only proceed when you intend to contact Telegram and incur configured provider costs:

1. Create a bot through Telegram's @BotFather. Obtain your own app API ID/hash from my.telegram.org. Bot-token mode needs both, as described in [Telethon's bot sign-in documentation](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in-as-a-bot-account). No userbot, phone-number login or OTP prompt is supported.
2. Edit the private JSON profile locally: set `owner_id` to your positive numeric Telegram **user** ID; set `telegram_api_id`, `telegram_api_hash`, `telegram_bot_token`, `provider_key`, an explicit `model` in `vendor/model` form, and `provider_enabled=true`. Leave disabled features disabled until needed. Do not put credentials in command history, issue reports, repository files or chat.
3. Install the adapter and validate offline:

   ```bash
   uv sync --locked --extra telegram
   uv run flux doctor --bot
   ```

4. Start only when authorized to connect:

   ```bash
   uv run flux bot start
   ```

Only incoming, non-forwarded, non-bot **private messages** from the configured sender in that same owner's private chat are accepted. Commands and approvals use the identical guard. Groups and channels are rejected. Messages are deduplicated durably, including after restart. A busy bot asks the owner to retry rather than accumulating an unbounded queue.

For the separately bounded live-smoke preparation, use the [private-input/offline-check runbook](docs/release/live-smoke-preparation.md). The normal bot/chat commands below are not the one-shot campaign runner.

## Local provider chat

```bash
uv run flux local chat --allow-remote
```

This command requires an explicitly configured/enabled provider. It reaches OpenRouter and can cost money. Local conversation uses isolated chat `0`; it does not reuse Telegram memory. There is no fake/demo production provider. Offline test doubles live only in `tests/`.

## Commands and tools

`/start`, `/help`, `/status`, `/status latency`, `/reset`, `/reset confirm`, `/approve TOKEN`. `/reset` first explains its scope; `/reset confirm` clears this chat's messages and summary. Notes, replay protection and receipts remain. Status exposes counts/latency, never conversation previews or identifiers.

| Tool | Default | Permission |
| --- | --- | --- |
| Current UTC time | enabled | READ_ONLY |
| AST numeric arithmetic | enabled | READ_ONLY; bounded syntax/depth/magnitude |
| Notes | enabled with confirmation | WRITE; exact content disclosed, 10-minute owner approval |
| File read | disabled | READ_ONLY; explicit root, descriptor-relative reads, secret/path/symlink checks |
| System information | disabled | READ_ONLY; minimal OS/Python versions |
| Brave web search | disabled | NETWORK; explicit API key, disclosed query and one-use approval |
| Shell / EXECUTE | removed / forbidden | no execution extension |

A model tool request cannot approve itself. Web/file content is untrusted data. Search uses a fixed Brave endpoint and never automatically fetches result URLs. Direct routing skips tool instructions; if tools are needed it switches to ReAct within the same budget. Web routing asks for query approval before any search or model generation; approved results return directly to the owner, with sources, without a hidden follow-up model call.

See [tool policy](docs/tool-policy.md), [architecture](docs/architecture.md), [memory/migration](docs/memory-and-migration.md), [provider controls/costs](docs/providers-and-costs.md), and [self-hosting, Docker, backup and restore](docs/self-hosting.md).

## Privacy and limitations

Conversation history, summaries, approvals, notes and Telegram sessions are private local data, **not encrypted at rest**. Backups and exports contain conversation data. Configured credentials and common token/password patterns are redacted at inference, transcript and reply boundaries, but no generic redactor can recognize every secret. Do not send secrets to the agent. Grant narrow read roots containing only files you consent to disclose.

Self-hosting does not make remote inference local: selected history and tool results can be sent to OpenRouter and its model provider. Brave receives approved search queries. Review their current terms, retention policies and prices yourself. Billing is reported as **unknown**, never zero. Each turn has hard call/tool/output/timeout bounds and a durable daily request ceiling; these are request limits, not a dollar-spend guarantee.

Telegram polling is outbound, with no HTTP listener. The running process still holds powerful credentials and network access; use a separate OS account or the restricted container. Host administrators and same-UID attackers remain trusted. Prompt injection may influence answer text; policy independently prevents unauthorized tools. A model's claim is not an action receipt.

Replayed/uncertain updates are never re-executed. A crash or Telegram delivery failure can therefore leave a completed action without a delivered reply. Inspect local receipts/notes rather than rearming an approval. SQLite is single-host storage; use one runtime instance and explicit retention/backup. No guarantee of autonomous task completion is made.

## Contributing and provenance

Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest -q`, and `uv run python scripts/security_gate.py`. CI and release gates are documented in [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the [release checklist](docs/release/RELEASE-CHECKLIST.md).

MIT project contributions: [LICENSE](LICENSE). Design influences from the original README: PicoClaw (modularity), OpenClaw (tool registry/ReAct), SkyClaw/Temm1e (conversation summarization). These are conceptual credits, not copied-source license grants. See [NOTICE](NOTICE), [provenance audit](docs/security-baseline.md) and the [actual production license inventory](docs/release/third-party-licenses.json).
