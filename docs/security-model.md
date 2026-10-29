# Security model

Protect the owner's provider quota, Telegram bot session, credentials, files, memory integrity and note actions. Adversaries include unauthorized Telegram senders, forwarded/group/channel/bot updates, replayed deliveries, a malicious model, and prompt injection inside search/file/memory data.

| Threat | Boundary | Regression evidence |
| --- | --- | --- |
| ACL bypass or command-prefix ambiguity | one sender+chat/private/incoming guard, exact command dispatch | test_identity; test_config_cli |
| Model self-approval or injected tools | strict JSON schema + capability policy + out-of-band owner command | test_tools; test_provider_core |
| Duplicate acknowledged write | durable update claim, one-use approval, atomic note publication | test_identity; test_tools |
| Shell or arithmetic resource abuse | execution tool removed; bounded numeric AST | test_tools; source gate |
| Traversal/symlink/hardlink/secret reads | explicit root, descriptor traversal, O_NOFOLLOW, file type/name/size checks | test_tools |
| Compressed/oversized provider or search responses | reject nonidentity encoding and oversized length before body, then cap streamed JSON bytes | test_http_boundaries |
| Partial/cross-chat memory writes | SQLite WAL/FULL, transactional scope, new-only restore | test_memory |
| Loss after failed summary | source snapshot + success-only summary transaction | test_memory |
| Quota abuse/fallback billing/auth loops | positive owner required, per-turn/daily calls, terminal error classes | test_provider_core |
| Logs/provider/answer credential leaks | no content logging, exact-key and common-pattern boundary redaction, static errors | test_provider_core |
| Concurrent bot sessions | CLI OS lock, existing session bot identity verification | test_config_cli; adapter tests |
| Supply-chain/private source publication | locked hashes, explicit Docker context, license/SBOM/secret/security gates | release evidence and checklist |

Trusted: operator, host administrator, same UID, explicitly edited private profile, installed dependencies and Telegram identity metadata from Telethon. This is not a sandbox for arbitrary Python plugins. No tool extension should be added without threat review. No firewall guarantee prevents a compromised Python process reaching the internet; the container reduces privileges and host filesystem access but runtime Telegram/provider traffic needs egress.

Private data is plaintext 0600 in 0700 directories. Existing insecure paths and symlinks are rejected rather than silently chmodded. Backups and explicit legacy imports/exports contain original conversation data. Redaction recognizes configured credentials/common forms, not every secret. Prompt injection can alter natural-language answers; treat only durable action receipts as evidence of completed actions. Host compromise, malicious dependencies, provider retention, operator misconfiguration and link phishing remain residual risks.

See [baseline/provenance](security-baseline.md). No exploit shell was run and no existing owner data was opened. Independent security review, live behavior and image signoff are separate release gates.
