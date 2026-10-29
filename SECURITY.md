# Security policy

FluxClaw v0.1.0 is an early source-only, single-owner personal preview. It is not a public-user service. Missing/zero owner ID fails closed. Groups, forwarded/bot/outgoing messages and unauthorized commands do not reach the model, tools or memory. No autonomous EXECUTE or shell tool exists.

## Security Notice — Review Before Self-Hosting

**Actual Telegram delivery and live model generation have not been verified for this release.** SPEC-001 remains 22 PASS / 0 FAIL / 2 BLOCKED: FLUX-04 and FLUX-24 remain BLOCKED. The owner authorized this limited source preview despite those open gates; this does not satisfy them. There is no independent security signoff or unrestricted production approval.

Offline tests, dependency/license checks and vulnerability/secret scans are evidence for their recorded source, image and date, not a guarantee of future safety or detection of every vulnerability. Remote offline/container CI passed with 252 tests; candidate image scans on 2026-10-29 reported zero known vulnerabilities and zero secrets. Consult the release notes for final run/commit identities and [verification](docs/release/verification.md) for scope and retained raw evidence. Source distribution does not confer Docker image security approval; no prebuilt image is included.

Please report suspected vulnerabilities privately to the repository owner using GitHub private vulnerability reporting if available; otherwise request a private channel without attaching secrets or exploit payloads to a public issue. Include affected commit, synthetic reproduction, expected/actual behavior and impact. Do not send live tokens, sessions, memory, note contents, provider bodies or raw debug logs. No response SLA or completed independent audit is claimed.

Review [threat model](docs/security-model.md), [tool boundaries](docs/tool-policy.md), [provider privacy/costs](docs/providers-and-costs.md) and [verification](docs/release/verification.md). Remote inference sends selected conversation/tool data outside the self-hosted machine. Provider terms/retention/costs are the operator's responsibility. Backups/session/config/memory are plaintext private local data, not encrypted vaults. Same-UID/administrator access and malicious installed dependencies are outside the policy boundary.

Prompt injection can affect answer text. Model claims do not authorize actions; only authenticated exact-content approval or an operator notes-only policy does. Redaction is defense in depth, not a promise to detect arbitrary secrets. Use a dedicated account/restricted container and narrow consented read roots. Never attach private state to a release or mount the host home into the container.

Local tests are deterministic offline fixtures. Actual Telegram+provider smoke, remote CI, independent security review and image/source publication approvals are separate gates. The source-only v0.1.0 authorization does not authorize live testing, image publication or deployment. Maintain the outstanding live and independent-review tasks in the [release checklist](docs/release/RELEASE-CHECKLIST.md).
