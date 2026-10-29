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
- [ ] Verify live unauthorized identity rejection, owner approval, notes durability, duplicate delivery behavior and budget caps without enabling public mode.
- [ ] Review remote GitHub CI on the exact source after a separately authorized push; local test PASS is not remote CI PASS.
- [ ] Operator explicitly approves source publication; source review does not imply image publication or deployment approval.
- [ ] Operator separately approves image publication/signing and deployment if desired. No auto-publish workflow exists.

Blocked live work does not require granting broad host access or relaxing ACL/tool checks. The minimal next permission is a bounded live bot+specified-model smoke with explicit generation/spend ceilings and owner identity, separately from push/publication/deployment.
