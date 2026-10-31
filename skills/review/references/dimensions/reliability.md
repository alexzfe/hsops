# Reliability

Does the server keep running, and recover by itself after a power cut or a reboot?

- **Restart policies:** every long-running container has `unless-stopped` or `always`.
- **Health checks:** critical apps have them, and dependent containers use `depends_on: condition: service_healthy`.
- **Boot:**
  - data mounts have `nofail` and a guard against writing into an unmounted mountpoint
  - Docker waits for its mounts
  - the firmware powers the machine on when power returns (ask if it can't be seen).
- **Single points of failure:**
  - if the server's own DNS (AdGuard or Pi-hole) dies, does the LAN have a fallback?
  - one disk holding everything
  - remote access with no backup path.
- **Recurring failures:** restart counts, failed units, and OOM kills in the history.
- **Power:** whether a UPS is present, and whether a graceful shutdown on low battery is configured (NUT). On a laptop, the battery acts as the UPS.
- **Heat:** temperatures under load; throttling.
