# Early source-only v0.1.0 — owner authorization and maintenance gates

On 2026-10-29 the owner explicitly authorized normal merge of PR #1, tag v0.1.0 on merged main and one GitHub **Pre-release**, titled `v0.1.0 — Initial FluxClaw Source Preview`, after final source/private-path/license checks and green CI. Only GitHub-generated source ZIP/tar.gz archives are included; no uploaded binaries, wheels or prebuilt images. Repository rules and any mandatory independent approval must be respected. No independent security signoff is claimed.

The owner accepts this early preview with **22 PASS / 0 FAIL / 2 BLOCKED**. FLUX-04 and FLUX-24 remain BLOCKED; publication does not constitute full SPEC-001 completion. This decision supersedes earlier publication holds only for this one source release. It does not authorize Telegram access, model generation, search, image publication or runtime deployment.

## Source distribution scope

Proposed: an exact reviewed Git source archive plus README/operating/security docs, LICENSE/NOTICE, dependency locks, actual Python dependency license inventory, source SBOM and verification records. Dockerfile/Compose may be included as source. Excluded: all private env files, credentials, owner/bot IDs, sessions, memory, notes, backups/volumes, runtime logs and prebuilt images. The operator's new input file is outside the repository; neither its contents nor private operator evidence belongs in CI artifacts or distribution.

## Owner checklist

- [x] Preserve all 24 FLUX statuses and distinguish fixture/actual live evidence: [verification.md](verification.md).
- [x] Genuine push/PR CI passed for source `0b8dc3405452faff9f4133044d558164a12285f3`: runs [40843691774](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40843691774) and [40843697225](https://github.com/hzjanuary/flux-ai-agent/actions/runs/40843697225), 252 tests. Earlier evidence remains in [remote-verification.json](remote-verification.json). Publication documentation must also pass final CI; inspect final identities in the release notes/operator evidence.
- [x] Download CI artifacts and validate GitHub ZIP SHA-256/CRC/paths, tar hash, source tree, every tracked byte/mode and image source/tree identity. Original failure logs and successful artifact bytes are preserved under `artifacts/remote-verification/` and GitHub Actions artifact IDs.
- [x] Preserve raw vulnerability scans and source/image SBOMs; automated scans at the recorded runs found zero vulnerabilities/secrets. Preserve actual dependency/license inventory and historical Gitleaks review/canary evidence without disabling scanners.
- [x] Owner authorizes sharing project contributions under MIT with LICENSE/NOTICE and applicable third-party attributions retained. Exact dependency license/version/text coverage is checked; Git authorship review is evidence, not a guarantee of copied-source absence. Community provenance review remains welcome.
- [ ] Independent security reviewer examines raw findings, residual risks and evidence scope. Passing automation is not an independent signoff.
- [x] Owner explicitly accepts a clearly disclosed early source preview with FLUX-04 BLOCKED. No real Telegram connection, generation or delivery has occurred.
- [ ] Owner reviews known limitations: plaintext local state/exports, host/same-UID trust, generic redaction limitations, remote provider retention/cost, request budgets not dollar guarantees, at-most-once uncertain delivery, single-host SQLite and dated scanner coverage.
- [ ] Verify final merged main SHA, tag target and GitHub-generated source archive bytes/modes/digests; record exact final CI and publication outcome in release notes/operator evidence. This pre-publication source checklist does not claim later events have happened.
- [x] Owner explicitly authorizes normal PR merge, v0.1.0 tag and one source-only GitHub pre-release. No bypass, force push, history rewrite or release beyond this scope.

## Docker image decision is separate

CI-built images were tested non-root/read-only, with dropped capabilities, no-new-privileges, private synthetic volume restart and no runtime network. The source and PR-merge image identities are recorded independently; PR merge trees were matched to the source. Raw OS/Python scan and image SBOM are preserved.

These results do not authorize prebuilt-image distribution. Image readiness still needs independent current vulnerability/license/runtime review, provenance/signing decisions and explicit operator publication/deploy permission. A source-only release must not claim that a prebuilt image is independently approved.

## Private disclosure and live hold

Follow [SECURITY.md](../../SECURITY.md) for private disclosure; never submit keys, sessions, owner/chat IDs, raw private conversations or unredacted evidence publicly.

The only selected live campaign is OpenRouter `openai/gpt-oss-20b:free`, maximum one generation and 128 output tokens, spend cap 0.00 USD. There are no retries, fallbacks, searches, summaries, tools or extra live recovery/ACL tests. Private input and evidence checks plus final named operator confirmation remain required. See [live-smoke-preparation.md](live-smoke-preparation.md); do not start the ordinary bot as a campaign shortcut.
