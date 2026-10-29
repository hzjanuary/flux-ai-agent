# Providers, limits and costs

The sole production inference adapter is OpenRouter's HTTPS `/api/v1/chat/completions`. No provider client is instantiated by imports, config init, doctor, tool-list or memory maintenance. Configure `provider_enabled=true`, a private `provider_key` and an explicit `model` (`vendor/model`) before a runtime action. Default has no model selection or fallback. `local chat` additionally requires `--allow-remote`. `bot start` is explicit network authorization for the configured bot's operation; project verification has not run it.

Model syntax is validated locally; actual model availability/support cannot be proven offline. A 404 is an unsupported-model terminal error rather than an invitation to select a different paid model. Authentication 401, billing 402, permission 403 and invalid request/output all stop. Only 408, 429, 5xx and transport/timeouts are fallback-eligible, and only if the operator sets `fallback_enabled=true` plus ordered `fallback_models`. No automatic repeated retry exists. The request explicitly disables OpenRouter's implicit provider fallback. Unsupported API extensions/errors are terminal. See [OpenRouter error documentation](https://openrouter.ai/docs/api_reference/errors-and-debugging.md) for the external contract; this project's exact status handling is tested with injected HTTP fixtures, not real generations.

| Setting | Default | Bound/meaning |
| --- | --- | --- |
| max_calls | 4 | 1–16 attempts shared by direct/ReAct/routing fallback/model fallback/summary |
| max_tool_calls | 3 | 1–8 proposals/executions per turn |
| max_output_tokens | 512 | 1–4096 requested output-token ceiling on every generation, including summaries |
| timeout | 20 | 1–120 seconds per model/tool network call, plus bounded whole-turn timeout |
| daily_calls | 100 | 1–100000 reserved attempts/day in UTC, transactionally persisted across restarts |
| history_limit | 20 | 1–100 recent messages sent as context; earlier source stays durable |
| summary_enabled | false | explicitly opt into another generation, within existing budgets |
| fallback_enabled | false | explicitly opt into provider/model privacy and cost changes |

Requests are reserved before dispatch; failed/timed-out attempts count, even if the provider did not bill. A crash after reservation does not refund calls. Daily limit is per local data store, not a multi-server/dollar budget; deleting the database or changing system time can defeat it. Billing stays **unknown**, not zero, regardless of fixture tests or model names containing `free`. Prices, terms and provider retention can change. Configure provider-side spend limits and review current terms separately.

Input is bounded to 8000 characters; memory context count, tool result size and remote response bytes are bounded. These character/request/output limits do not guarantee a fixed dollar charge; tokenization, provider reasoning/internal usage and pricing vary. No price polling, billing enablement, inference, model download or provider credential validation is performed by offline commands.

Web search optionally uses the [Brave Search API](https://api-dashboard.search.brave.com/app/documentation/web-search). Set web_enabled=true and a private web_key. Exact query and result count are shown before a one-use owner approval. Brave may bill searches separately; model daily_calls does not count search requests, which are separately limited by tool count/approval and network timeout. Approved results are returned directly, so there is no hidden post-approval generation. No arbitrary URL crawler is included.
