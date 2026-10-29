# Self-hosting and container operations

Linux with Python 3.12+ and an ordinary CPU. Run a dedicated OS account, keep config/data private and use a local persistent filesystem. uv installs the hash-locked dependencies; Telethon is optional for offline use. No server, HTTP port, GPU, Redis, mandatory external state service or model download is needed. Offline doctor does not authenticate credentials or contact Telegram/providers.

See README for owner-ID and bot-token setup. Explicitly start only after provisioning and authorizing Telegram/provider traffic. File permissions are checked; existing insecure paths are refused, never automatically changed. Runtime and local maintenance share a nonblocking lock; stop the bot before import/reset/backup. Configure retention and private backups before a long-running bot.

## Optional Docker

Dockerfile pins both base images by digest and installs the locked production closure into a virtualenv. The final image runs uid/gid 10001, includes LICENSE/NOTICE and actual third-party license texts, and contains no owner settings, sessions, memory or host home mounts. `.dockerignore` permits only build inputs, including flat package Python modules; ignored caches/private package data are excluded. No image is automatically published.

Build and initialize a **new** private volume (these commands download/build packages, not models):

```bash
docker build --build-arg SOURCE_REVISION="$(git rev-parse HEAD)" -t fluxclaw:local .
docker volume create fluxclaw-local-data
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  -v fluxclaw-local-data:/data fluxclaw:local config init --data-dir /data
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  -v fluxclaw-local-data:/data fluxclaw:local doctor
```

The image's /data directory seeds a newly created volume with uid 10001 and mode 0700. Existing volumes with incompatible permissions fail closed; provision a separate volume rather than changing owner data. Config init is non-overwriting and creates /data/config.json mode 0600. The default image command is doctor, never bot start. Run memory list/backup/export in the same restricted shape; only the selected volume is mounted.

Provision secrets locally in the private volume through your operator-managed secret workflow, or mount a dedicated reviewed 0600 profile and use supported environment overrides. Do not bake credentials into the image or run them through a public command transcript. The profile's data_dir must be /data for this volume. The container UID must own/read the selected profile. Doctor validates all startup fields without connecting.

Compose supplies the same non-root/read-only/cap-drop/no-new-privileges restrictions, a 16 MB noexec tmpfs, pids/memory/CPU limits, a private named volume and no published ports. It has an explicit `bot` profile. Initialize its separate Compose volume before startup:

```bash
docker compose --profile bot run --rm --no-deps bot config init --data-dir /data
docker compose --profile bot run --rm --no-deps bot doctor --bot
```

These operations do not start the bot. After privately provisioning config and explicitly approving live outbound traffic:

```bash
SOURCE_REVISION="$(git rev-parse HEAD)" docker compose --profile bot up --build
```

Telegram and OpenRouter/optional Brave require outbound internet at runtime; the offline network-none smoke cannot prove their live availability. Compose publishes no inbound service but is not an egress firewall. Never mount the Docker socket, host root, arbitrary home directories or legacy owner data into the bot. A source-preview test is not image-publication/security approval.

## Recovery and release evidence

Use `flux memory backup` while bot is stopped, then `memory restore` into a new directory/volume. [Memory documentation](memory-and-migration.md) gives exact commands and non-overwriting semantics. Keep private backups off the release path. Synthetic offline container restart proof and exact image identity appear in [verification](release/verification.md); live Telegram/provider smoke stays BLOCKED until separately authorized. See [release checklist](release/RELEASE-CHECKLIST.md) before publication.
