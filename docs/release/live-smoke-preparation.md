# One bounded live-smoke campaign — BLOCKED before access

Operator selection: OpenRouter, exact model `openai/gpt-oss-20b:free`, at most **one generation request**, at most **128 output tokens**, maximum **0.00 USD**. No retry, fallback, search, summarization, tools, filesystem tools, background calls, billing activation or paid upgrade. Only one synthetic owner-private-message exchange is proposed. No Telegram connection, bot login, generation or delivery has occurred.

## Private inputs on Linux Mint

A non-overwriting blank template is prepared at `~/.config/fluxclaw-live-smoke/private.env`, owned by the operator, file 0600 and directory 0700. Actual credentials and owner/bot IDs stay private. Edit locally:

```bash
nano ~/.config/fluxclaw-live-smoke/private.env
stat -c '%a %n' ~/.config/fluxclaw-live-smoke ~/.config/fluxclaw-live-smoke/private.env
```

Do not paste values into chat, use them as command-line arguments, print the file, commit it, or `source` it. The checker reads literal assignment data and never evaluates shell expressions. No existing production profile, Telegram session or conversation is reused. Existing templates are never overwritten by initialization.

The **six native overrides** accepted by `flux.config.load` are:

| Field | Enter privately |
| --- | --- |
| TELEGRAM_API_ID | Telegram app ID required by Telethon |
| TELEGRAM_API_HASH | Telegram app hash |
| TELEGRAM_BOT_TOKEN | Token issued for the dedicated test bot |
| TELEGRAM_OWNER_ID | Intended positive owner user ID |
| OPENROUTER_API_KEY | Separately scoped test-provider key |
| DEFAULT_MODEL | Already set to the exact operator-selected model; no substitution |

The normal application loads a private JSON profile and **does not load `.env` automatically**. `provider_enabled`, budgets and feature flags are JSON settings, not additional supported runtime environment overrides. Do not invent/export unsupported MAX_TOKENS/PROVIDER_ENABLED variables and assume they enforce the campaign.

The additional fields in this template are consumed **only by `scripts/live_smoke_preflight.py`**:

- `SMOKE_EXPECTED_BOT_ID` and `SMOKE_EXPECTED_BOT_USERNAME`: intended dedicated identity, entered privately; bot ID must agree with token prefix. This is a consistency check, not remote authentication.
- `SMOKE_MAX_GENERATION_REQUESTS=1`, `SMOKE_MAX_OUTPUT_TOKENS=128`, `SMOKE_MAX_SPEND_USD=0.00`: fixed declared campaign policy; any change fails the offline check.
- `SMOKE_DEDICATED_TEST_BOT_CONFIRMED`, `SMOKE_BOT_IDENTITY_CONFIRMED`, `SMOKE_CREDENTIAL_SCOPE_CONFIRMED`, `SMOKE_MODEL_ACCESS_CONFIRMED`, `SMOKE_BILLING_ZERO_SPEND_CONFIRMED`, `SMOKE_PRIVACY_CONFIRMED`: start as `false`; set `true` only after personally checking the named bot/account/provider conditions.
- `SMOKE_OPERATOR_EVIDENCE_FILE`: a separate, nonempty private 0600 operator record/export referencing verified bot identity, key scope, exact-model access/128-token support, zero-spend controls and reviewed provider privacy conditions. The checker checks file permissions/presence, **not its truth or freshness**; evidence still requires manual review.

## Offline check — safe to run now

From the repository root:

```bash
uv run python scripts/live_smoke_preflight.py
```

No client, provider, tool registry, store or session is instantiated. It reads only the explicitly selected private input file, checks known fields/types, permissions, the fixed policy, identity consistency and operator confirmations, and prints field names/status only. Ambient production credential variables are ignored. Empty or unconfirmed inputs return exit 2, without printing values. Complete structural input can return exit 0, **while remaining BLOCKED_BEFORE_LIVE**.

The script has **no live command or execution flag**. It does not prove that credentials authenticate, that the model is currently available to that account, or that billing/privacy terms meet the policy. The `:free` suffix and a local confirmation are **not proof of a zero charge**. Unknown identity, access, billing, output-token support or privacy conditions prohibit any live request.

## Final hold before a future campaign

**STOP after the offline check.** Do not run the regular `flux bot start` or `flux local chat`: their per-turn budgets and enabled read-only tools are not the proposed campaign's durable one-attempt/no-tool execution control.

Before any live access, review the private evidence and obtain the operator's final confirmation of the named bot, owner, exact model, zero-spend conditions and isolated storage. A separately reviewed one-shot execution path must reserve the campaign's sole attempt durably before dispatch, disable every tool/follow-up call, accept only the one authorized synthetic private input, send the real adapter response through Telegram, record sanitized reported usage/delivery/provenance, stop the bot, and never retry an uncertain request. No live runner is launched or approved by this preparation.

Do not perform extra live unauthorized-event, approval or recovery tests. Their existing offline evidence stays separate. No merge, tag, release, prebuilt image publication, remote deployment or independent security signoff follows from this campaign.
