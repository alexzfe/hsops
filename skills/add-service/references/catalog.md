# App catalog

The options for each category and when each one fits. These are starting points for the conversation, not defaults. Ask what the user needs, then recommend from here, or beyond this list when nothing fits.

| Category | Options | Fits when |
|---|---|---|
| Photo library | **Immich** | They want a Google Photos replacement: phone backup, faces, search. Needs about 4 GB of RAM or more for machine learning. |
| | **PhotoPrism** | They're browsing an existing archive more than backing up phones. Lighter. |
| Media server | **Jellyfin** | They want it free and open, hardware transcoding included, with no account. |
| | **Plex** | Family members want polished clients and easy sharing. Hardware transcoding needs Plex Pass. |
| | **Emby** | They're in between: polished, with a paid tier. |
| Media automation | **Sonarr / Radarr / Prowlarr** | Only when they ask for it. Pair it with a download client. |
| File sync / cloud | **Syncthing** | They want folder sync between devices, with no server UI. |
| | **Nextcloud** | They want a full suite: files, calendar, contacts. Heavier and needs more upkeep. |
| | **Seafile** | They want fast file sync with a web UI, and less than Nextcloud. |
| Passwords | **Vaultwarden** | They want a self-hosted Bitwarden server. Keep it on the tailnet and back it up. |
| Documents | **Paperless-ngx** | They want to scan paper, OCR it and search it. |
| Home automation | **Home Assistant** | They want smart-home control. Zigbee or Z-Wave dongles need USB passthrough or host networking. |
| Network ad blocking / DNS | **AdGuard Home**, **Pi-hole** | They want LAN-wide ad blocking. If it goes down, DNS for the whole LAN goes down with it, so set a fallback DNS on the router. |
| Dashboard | **Homepage**, **Homarr** | They're running about four or more apps. |
| Reverse proxy | **Caddy**, **Traefik**, **Nginx Proxy Manager** | They need public URLs or HTTPS names on the LAN. Not needed for tailnet-only use (`tailscale serve`). |
| Monitoring / backups | see the `monitoring` and `backups` skills | |
