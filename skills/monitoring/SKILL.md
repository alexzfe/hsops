---
name: monitoring
description: Use when adding or extending monitoring on the homeserver, such as uptime checks, alerts and phone notifications, dashboards, host and container metrics, disk and SMART health, or backup heartbeats.
---

# Monitoring

Monitoring is worth having for the failures that would otherwise go unnoticed: a disk filling up, a drive dying, a service down for days, a backup that quietly stopped. Read `../../shared/conventions.md` (relative to this skill's directory) first, load the server's context, and check the profile's Monitoring section for what already exists.

1. **Agree on coverage** with the user, in this priority order:
   1. A notification channel the user actually sees. None of the checks below reach the user without one.
   2. An up check for every row in the Services table.
   3. A disk space alert.
   4. Drive health (SMART) on every physical disk.
   5. Backup freshness: a heartbeat that alerts when a backup *doesn't* report in.
   6. Host and container metrics with history.
2. **Choose tools with the user.** Count the hosts from the data folder's `servers/`. In a Discovery round (conventions), cover how much they want to run and learn, and whether they want dashboards. Then discuss what fits:

   | Need | Options |
   |---|---|
   | Notifications | ntfy (self-hosted or ntfy.sh), Gotify, Telegram or Discord bots, email |
   | Up checks and heartbeats | Uptime Kuma, Gatus, Healthchecks |
   | Host and container metrics | Beszel (light), Netdata (zero-config, rich), Prometheus + node-exporter + cAdvisor + Grafana (powerful, heavy, worth it for several hosts or for learning) |
   | Drive health | smartd from smartmontools; Scrutiny for a web UI |

   A monitor running on the server can't report the server being down. Offer an outside check: a second device, an external uptime ping, or a heartbeat that alerts when it stops arriving.
3. **Deploy** the containers with `add-service`, and install host daemons such as smartd natively.
4. **Test every alert path.** Send a test notification, stop a container and watch its alert arrive, fire SMART's test alert (smartd `-M test`), and withhold a heartbeat.
5. **Record** in the profile's Monitoring section what is checked, by which tool, and where alerts go. Add a line to `changelog.md`.

**Done when:** each coverage item the user chose has a check, each check has been seen to alert on the user's device, and the profile records it all.
