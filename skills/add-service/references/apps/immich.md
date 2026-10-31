# Immich

## Deploy

- **Source of truth:** the `docker-compose.yml` and `example.env` attached to the latest GitHub release (`https://github.com/immich-app/immich/releases/latest/download/<file>`). Use them as-is apart from the `.env` values.
- **Version:** pin `IMMICH_VERSION` to a release. Immich ships breaking changes often and announces them in the release notes, so read every note between the current and target version before upgrading.
- **Storage:** put `DB_DATA_LOCATION` (Postgres) on a local SSD, never on a network share. Put `UPLOAD_LOCATION` on the photo disk.
- **Hardware acceleration:** enable it for machine learning and video transcoding with the `hwaccel.*.yml` files from the same release.
- **Port:** 2283. Point the mobile app at the tailnet name, e.g. `http://<server>:2283`, so phone backup works away from home.

## Review checks

- `IMMICH_VERSION` is pinned, not `release`, and is no more than a few releases behind.
- The database is on an SSD.
- Backups cover both `UPLOAD_LOCATION` and the database dumps Immich writes under `UPLOAD_LOCATION/backups`. Photos without the database lose albums, people and metadata.
- Machine learning isn't getting OOM-killed (`docker inspect` → `OOMKilled`). On hardware with little RAM, consider moving machine learning to another machine or turning it off.
