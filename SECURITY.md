# Security policy

FluxClaw v0.1 is a single-owner personal source preview. It is not a public-user service. Missing/zero owner ID fails closed. Groups, forwarded/bot/outgoing messages and unauthorized commands do not reach the model, tools or memory. No autonomous EXECUTE or shell tool exists.

Please report suspected vulnerabilities privately to the repository owner using GitHub private vulnerability reporting if available; otherwise request a private channel without attaching secrets or exploit payloads to a public issue. Include affected commit, synthetic reproduction, expected/actual behavior and impact. Do not send live tokens, sessions, memory, note contents, provider bodies or raw debug logs. No response SLA or completed independent audit is claimed.

Review [threat model](docs/security-model.md), [tool boundaries](docs/tool-policy.md), [provider privacy/costs](docs/providers-and-costs.md) and [verification](docs/release/verification.md). Remote inference sends selected conversation/tool data outside the self-hosted machine. Provider terms/retention/costs are the operator's responsibility. Backups/session/config/memory are plaintext private local data, not encrypted vaults. Same-UID/administrator access and malicious installed dependencies are outside the policy boundary.

Prompt injection can affect answer text. Model claims do not authorize actions; only authenticated exact-content approval or an operator notes-only policy does. Redaction is defense in depth, not a promise to detect arbitrary secrets. Use a dedicated account/restricted container and narrow consented read roots. Never attach private state to a release or mount the host home into the container.

Local tests are deterministic offline fixtures. Actual Telegram+provider smoke, remote CI, independent security review and image/source publication approvals are separate gates. No push, release, image publication or bot deployment is implied by green local tests. See the release checklist for uncompleted gates.
