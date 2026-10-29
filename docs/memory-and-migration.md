# Memory and migration

SQLite schema version 1, WAL mode, FULL synchronous commits, per-chat ordered appends and transactional usage/approvals/dedup. Default context includes at most `history_limit` messages; older unsummarized messages stay on disk. Summaries are disabled unless `summary_enabled=true` and an explicit `summary_model` is configured. They run asynchronously **inside** a serialized turn, sharing its request budget; failure/exhaustion retains all source and the prior summary. Success commits summary + removes exactly its unchanged selected source atomically. No background summarizer is launched at import/startup.

Use the local CLI, with the bot stopped (the same private runtime lock prevents concurrent maintenance):

```bash
flux memory list
flux memory status --chat 123456789
flux memory export --chat 123456789 --output /absolute/private/export.json
flux memory backup --output /absolute/private/backup.sqlite3
flux memory reset --chat 123456789 --confirm
flux memory retain --chat 123456789 --keep 1000 --confirm
```

List/status show counts and IDs for the local operator only; Telegram status omits IDs/content. Exports and backups are private 0600, **new destination only**. They contain conversation/approval data; encrypt them separately if required. Reset clears both messages and summary, plus pending approvals for that chat. Notes, import markers, dedup records and action receipts survive so reset cannot replay writes. Retain explicitly deletes older messages for only the selected chat; it is never an automatic response to summary failure. SQLite deletion is logical; forensic erasure of backups, WAL and filesystem media is not guaranteed.

To restore a validated schema-v1 backup into a **new** database:

```bash
flux memory restore --source /absolute/private/backup.sqlite3 \
  --output /absolute/private/recovered/memory.sqlite3 --confirm
```

Restore checks integrity and refuses any existing destination. Point a separately reviewed private profile's data_dir to that new directory; inspect status before starting. Do not copy a live SQLite file without its WAL; use the backup API. Store data on a local filesystem, not a shared network filesystem, and run one bot/runtime per data directory.

Legacy `fluxclaw_memory.json` is never read automatically, moved or deleted. Preview only synthetic or intentionally selected owner data locally:

```bash
flux memory import --source /absolute/private/fluxclaw_memory.json --chat 123456789
```

Only a message count and summary-presence flag are printed. To import exactly that chat into an empty chat once:

```bash
flux memory import --source /absolute/private/fluxclaw_memory.json --chat 123456789 \
  --backup /absolute/private/legacy-original-backup.json --confirm
```

Source schema, roles and lengths are validated; a private byte-for-byte source backup is created before the transactional import; source bytes stay unchanged. Each content digest/chat is recorded to prevent re-import even after reset. The import does not merge into nonempty state. Other legacy chats are never imported implicitly. Cancel by omitting --confirm; the source remains untouched. Imported/exported data and raw backups can include historical secrets, so protect them; outbound prompts still pass the redactor.

Delivery semantics: update claim is committed before processing; reply state is committed before sending. A crash can leave a processing claim with an uncertain outcome. It will not be rerun automatically. Approval is consumed before effects. Atomic notes survive restart, but network failures or delivery failures cannot guarantee a visible reply. Inspect receipts and notes before proposing a new action; never manually rearm a consumed approval.
