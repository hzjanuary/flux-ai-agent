# Preserved baseline and provenance

Reviewed all 11 reachable baseline commits, 71 objects, 50 source blobs and every current Python module. All commits are attributed to repository owner hzjanuary / Hoang Nguyen; origin is hzjanuary/flux-ai-agent. The initial commit introduces the same Python modules. No vendored upstream source, copyright header or separate third-party code attribution was found. README names PicoClaw, OpenClaw and SkyClaw/Temm1e as design influences; these credits will be retained. This is Git provenance evidence, not a guarantee of authorship. Operator source-publication review remains required. MIT is granted for this repository's contributions on this basis; third-party libraries retain their own licenses.

Metadata-only private-path inventory found no .env, session, legacy memory or notes in this checkout. No owner data was read or modified. A full reachable-blob credential-pattern audit found eight occurrences in historical example files; each is a repeated-character synthetic bot-token example. No confirmed credential found by these patterns. No history rewrite performed. Pattern scanning does not prove absence of all secrets.

Static behavioral contracts at 0eb150a:

- owner=0 returns True (public), commands use loose prefix handlers; ordinary events resolve senders before ACL.
- shell tool accepts prefixes and invokes a shell; read_file accepts arbitrary paths; arithmetic calls eval.
- tool arguments/results and prompts reach logs, exception strings can reach replies.
- import constructs config and provider/Telegram clients, requiring real credentials.
- shared JSON persistence is read/modify/write; failed summary still removes old messages.
- fallback uses error substrings; no shared total budget or durable duplicate suppression.

These are observed source behaviors, not executed exploit tests. Refactor negative tests must exercise replacement public entry points, including every command and plain events, and demonstrate no model, memory or tool access for unauthorized identities. No shell exploit is run on the host.
