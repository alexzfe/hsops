# Plex

## Deploy

- **Image:** `plexinc/pms-docker` or `lscr.io/linuxserver/plex`. Use `network_mode: host`; it's the simplest way to get local discovery and direct connections working.
- **Claiming:** a `PLEX_CLAIM` token from plex.tv/claim expires about 4 minutes after it's issued. Fetch it right before the first `docker compose up`.
- **Hardware transcoding** requires Plex Pass. Device and GPU setup is the same as in `jellyfin.md`.
- **Library naming:** same scheme as Jellyfin.

## Review checks

- With Tailscale in use, `100.64.0.0/10` is listed under Settings → Network → "LAN Networks". Without it, Plex treats tailnet clients as remote and routes them through its relay or limits their bandwidth.
- Hardware transcoding is enabled and shows "(hw)" on the dashboard during a transcode, if the user has Plex Pass.
