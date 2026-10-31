# Jellyfin

## Deploy

- **Image:** `jellyfin/jellyfin`. **Port:** 8096.
- **Media:** mount the media paths read-only (`:ro`). Jellyfin needs write access only to its own `config` and `cache` volumes.
- **Hardware transcoding:**
  - Intel: add `devices: [/dev/dri:/dev/dri]` and `group_add: ["<render GID>"]`, using the numeric GID from `getent group render`. Then enable QSV or VAAPI under Dashboard → Playback.
  - NVIDIA: add the `deploy.resources.reservations.devices` GPU block and select NVENC.
- **Library naming** decides whether metadata matches: `Movies/Title (Year)/Title (Year).mkv` and `Shows/Title/Season 01/Title S01E01.mkv`.

## Review checks

- Hardware transcoding is actually in use: during a forced transcode, the dashboard shows the stream as hardware (HW), and the logs mention `qsv`, `vaapi` or `nvenc`.
- The media mounts are `:ro`.
- The cache volume is on an SSD, or at least not on the same spinning disk as the media.
