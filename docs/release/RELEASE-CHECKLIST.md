# Release checklist — operator review required

Local evidence and authorization are separate. A PASS may concern only fixture/offline behavior. Keep plan ACTIVE for every unmet gate.

- [ ] Review full provenance/ownership evidence, MIT grant, NOTICE and all dependency license texts; resolve any copied-source uncertainty.
- [ ] Confirm exact clean source SHA and source-archive hash; inspect current source/path/credential/history scanner reports.
- [ ] Run locked install, lint/format/types, all offline security/integration tests and isolated clean first run.
- [ ] Audit runtime and development dependencies; review dated raw vulnerability reports and SBOM.
- [ ] Build exact source image with digest-pinned bases; record image ID/source label and inspect all filesystem/layers for private paths/secrets.
- [ ] Verify uid 10001, read-only root, cap-drop/no-new-privileges, no ports, private persistent volume restart and invalid bot-start refusal under network none.
- [ ] Independently review current OS+library image scan results, unresolved CVEs/licenses and actual image SBOM before image-readiness signoff.
- [ ] Obtain separate authorization and provision synthetic/private owner credentials for an actual one-owner Telegram+LLM exchange. Record exact model, provider generation count/cost unknown, source/image identity and redacted result. Do not publish credentials/IDs/text.
- [x] Preserve offline unauthorized identity, approval, notes durability, duplicate delivery and budget evidence separately; no additional live tests are authorized in the selected campaign.
- [ ] Review remote GitHub CI on the exact source after a separately authorized push; local test PASS is not remote CI PASS.
- [ ] Operator explicitly approves source publication; source review does not imply image publication or deployment approval.
- [ ] Operator separately approves image publication/signing and deployment if desired. No auto-publish workflow exists.

Blocked live work does not require granting broad host access or relaxing ACL/tool checks. The minimal next permission is a bounded live bot+specified-model smoke with explicit generation/spend ceilings and owner identity, separately from push/publication/deployment.

## Current authorized scope supersedes future/live checklist suggestions above

See [source-only-v0.1.0.md](source-only-v0.1.0.md) for the proposed source-only owner decision. Ordinary feature-branch push, one Draft PR and remote CI are now authorized. Automated CI/source/image gates have actual passing evidence at a143673; independent signoff and publication are still not granted.

The selected live scope is exactly one synthetic private exchange using OpenRouter openai/gpt-oss-20b:free, one generation/128 output tokens/0.00 USD, after private evidence review and final named confirmation. **Do not perform the additional live unauthorized-event, approval, note/restart or recovery tests mentioned in the historical checklist above.** Preserve their existing offline coverage instead. Do not merge/tag/release/publish/deploy automatically after Phase A/C or preflight.
