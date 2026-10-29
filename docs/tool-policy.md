# Tool policy

All model calls enter `Registry.execute`; no decorator or prompt can grant authority. The static registry declares READ_ONLY, NETWORK, WRITE or EXECUTE. EXECUTE is categorically denied and no shell tool exists. Unknown tools, additional properties, booleans-as-integers, wrong types, excessive text and invalid ranges fail before execution.

| Capability | Runtime policy |
| --- | --- |
| READ_ONLY | Only enabled built-ins; time + arithmetic default; files/system info require operator config |
| WRITE | Durable exact-argument owner approval, or explicit operator `notes_preapproved=true` limited to notes |
| NETWORK | `web_enabled=true` + `web_key` + exact-query one-use owner approval every time |
| EXECUTE | always denied; no extension or shell flag |

Approval tokens are random 96-bit values, bound to chat/name/immutable JSON arguments, expire after 600 seconds, and persist across restart. The owner sees all proposed content/query and `/approve TOKEN`. The authenticated owner command consumes approval before action; failure or crash cannot rearm it. A model can neither supply an approval argument nor call the approval API. Current feature flags/schema are checked again at confirmation. Receipts contain tool/action state, not note/query content. Pending approvals necessarily contain private proposed arguments and stay in the private database.

Notes use a separate 0700 data/notes directory, 0600 temporary files, fsync, atomic non-overwriting publication and directory fsync. Names derive from chat/action identity, not user paths; title allows only ASCII letters/digits/_/- up to 64 chars; content is bounded. Retried deterministic actions verify existing content instead of overwriting a collision. Known secret-like text is rejected before write/network proposals.

File reads require an operator `read_root`. Caller paths must be relative, without hidden or parent components. Secret/config/memory/session/key names and key/database extensions are blocked. Private data root is blocked. Each path component is opened relative to a pinned directory descriptor with O_NOFOLLOW, and the final file must be a regular, single-link UTF-8 file at most 16000 bytes. Symlinks, hardlinks, directories, FIFOs and sockets fail. Host administrators and malicious same-UID filesystem modifications are outside the boundary; do not share writable roots with an attacker.

Arithmetic accepts only numeric constants, + - * / // % and bounded **, with 256 characters, 64 AST nodes, depth 12, finite magnitude at most 10^12, exponent magnitude at most 12 and power-base magnitude at most 10^6. Calls, attributes, strings, containers, names, comprehensions and boolean values fail. Python eval/exec is never used.

Brave search uses HTTPS to a fixed endpoint; 1–5 results, query <=256 chars, bounded snippets/body, timeout, no redirects, no proxy environment and no URL follow-up. Approved search results go directly to the owner as lower-trust data; no hidden model call follows. Web responses can contain malicious instructions or deceptive links. No search request is made by tests/doctor/imports.
