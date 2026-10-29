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

## Early source-only v0.1.0 authorization supersedes historical holds above

The owner explicitly authorized one early source-only v0.1.0 GitHub pre-release through the normal PR #1 merge workflow, after final candidate gates. See [source-only-v0.1.0.md](source-only-v0.1.0.md). Green remote source/image CI is automated evidence, not independent signoff. Maintain **22 PASS / 0 FAIL / 2 BLOCKED**; source publication cannot clear FLUX-04 or FLUX-24.

- [x] Owner accepts a source preview despite the blocked live and independent-review criteria; MIT/NOTICE/third-party attributions remain included.
- [ ] Verify final candidate push/PR CI, merge result, main SHA, v0.1.0 tag, generated ZIP/tar.gz private-path/content checks and Pre-release flag. Actual completion is recorded in release notes/operator evidence after publication.
- [ ] Maintenance: conduct only the separately approved bounded live smoke after private identity/account/billing/privacy review and final named confirmation. Keep actual evidence separate from fixtures.
- [ ] Maintenance: obtain independent security/ownership review and complete all original FLUX-24 conditions; retain dated raw scan/history/license evidence and known limitations.
- [ ] Any future image publication or deployment needs a separate decision and current image-security review. No image is distributed in this source release.

The selected live scope is exactly one synthetic private exchange using OpenRouter openai/gpt-oss-20b:free, one generation/128 output tokens/0.00 USD, after private evidence review and final named confirmation. **Do not perform the additional live unauthorized-event, approval, note/restart or recovery tests mentioned in the historical checklist above.** Preserve their existing offline coverage instead. Source publication does not authorize live execution or another development/deployment campaign.
