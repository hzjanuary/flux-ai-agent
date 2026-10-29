# Proposed source-only v0.1.0 owner decision — NOT APPROVED

This is a decision package, not a release instruction. Ordinary feature-branch push, one Draft PR and genuine CI were authorized. Merge, tags, GitHub releases, prebuilt Docker images and remote deployment are not authorized. No independent security signoff is claimed.

## Source distribution scope

Proposed: an exact reviewed Git source archive plus README/operating/security docs, LICENSE/NOTICE, dependency locks, actual Python dependency license inventory, source SBOM and verification records. Dockerfile/Compose may be included as source. Excluded: all private env files, credentials, owner/bot IDs, sessions, memory, notes, backups/volumes, runtime logs and prebuilt images. The operator's new input file is outside the repository; neither its contents nor private operator evidence belongs in CI artifacts or distribution.

## Owner checklist

- [x] Preserve all 24 FLUX statuses and distinguish fixture/actual live evidence: [verification.md](verification.md).
- [x] Genuine push/PR CI passed for source `a143673c534b2c43f4b89c5e04a99622625a884d`: [remote-verification.json](remote-verification.json). Final delivery HEAD must also retain green required jobs; inspect exact final run IDs in the owner evidence.
- [x] Download CI artifacts and validate GitHub ZIP SHA-256/CRC/paths, tar hash, source tree, every tracked byte/mode and image source/tree identity. Original failure logs and successful artifact bytes are preserved under `artifacts/remote-verification/` and GitHub Actions artifact IDs.
- [x] Preserve raw vulnerability scans and source/image SBOMs; automated scans at the recorded runs found zero vulnerabilities/secrets. Preserve actual dependency/license inventory and historical Gitleaks review/canary evidence without disabling scanners.
- [ ] Owner reviews source authorship/MIT grant, NOTICE/credits and all actual dependency license terms. Git authorship review is evidence, not a guarantee of copied-source absence.
- [ ] Independent security reviewer examines raw findings, residual risks and evidence scope. Passing automation is not an independent signoff.
- [ ] Owner explicitly decides whether to require FLUX-04 live PASS before a source release or accept a clearly disclosed source preview with FLUX-04 BLOCKED. Current state: no real Telegram connection, generation or delivery.
- [ ] Owner reviews known limitations: plaintext local state/exports, host/same-UID trust, generic redaction limitations, remote provider retention/cost, request budgets not dollar guarantees, at-most-once uncertain delivery, single-host SQLite and dated scanner coverage.
- [ ] Owner selects the exact release commit/archive and verifies its digest and green required CI. Draft PR remains unmerged; no tag/release is created by this checklist.
- [ ] Owner separately authorizes any merge/tag/GitHub release and approves source-only distribution. No authorization is implied here.

## Docker image decision is separate

CI-built images were tested non-root/read-only, with dropped capabilities, no-new-privileges, private synthetic volume restart and no runtime network. The source and PR-merge image identities are recorded independently; PR merge trees were matched to the source. Raw OS/Python scan and image SBOM are preserved.

These results do not authorize prebuilt-image distribution. Image readiness still needs independent current vulnerability/license/runtime review, provenance/signing decisions and explicit operator publication/deploy permission. A source-only release must not claim that a prebuilt image is independently approved.

## Private disclosure and live hold

Follow [SECURITY.md](../../SECURITY.md) for private disclosure; never submit keys, sessions, owner/chat IDs, raw private conversations or unredacted evidence publicly.

The only selected live campaign is OpenRouter `openai/gpt-oss-20b:free`, maximum one generation and 128 output tokens, spend cap 0.00 USD. There are no retries, fallbacks, searches, summaries, tools or extra live recovery/ACL tests. Private input and evidence checks plus final named operator confirmation remain required. See [live-smoke-preparation.md](live-smoke-preparation.md); do not start the ordinary bot as a campaign shortcut.
