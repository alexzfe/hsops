---
name: diagnose
description: Diagnose and fix problems on the homeserver, such as a service down, a container crash-looping, an app unreachable, a full disk, a slow server, or a failed update. Use when something on the homeserver is broken, erroring, slow or behaving unexpectedly.
---

# Diagnose

Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context. Check the recent `changelog.md` entries first, because most breakage follows a change.

1. **Pin the symptom.** Establish what exactly fails, since when, and for whom: one device or everyone, LAN or tailnet. Reproduce it yourself where you can, for example with `curl` or `docker compose ps`.
2. **Scope it.** Decide whether the problem is host-wide or limited to one service. Run the host checks in one batch: `df -h; df -i; free -h; uptime; systemctl --failed; docker ps -a --format '{{.Names}}\t{{.Status}}'; journalctl -p err -b --no-pager | tail -50; sudo -n dmesg -T | tail -30`.
3. **Narrow down to the service.** Collect:
   - logs from `docker compose logs --tail=200`
   - container state from `docker inspect` (`ExitCode`, `OOMKilled`, `RestartCount`, health)
   - listening ports from `ss -tlnp`
   - whether the service is reachable from the server itself and from the client.
   
   If the app has a file under `../add-service/references/apps/`, read it.
4. **Form a hypothesis.** It must explain *all* the evidence. Confirm it with a read-only check before changing anything.
5. **Fix the cause.** Make the smallest change that addresses the cause rather than the symptom, following the fixed rules. Restarting a crash-looping container is not a fix.
6. **Verify.** Rerun the step 1 reproduction; it must now pass.

**Done when:** the root cause is named along with the evidence that proves it, and the step 1 reproduction passes. If the cause stays unknown, the task is done when each ruled-out cause is listed with its evidence and the user has the next check to run.

## Common causes

Most homeserver incidents are one of these. Test each against the evidence.

- **Disk or inodes full:** databases corrupt and containers fail to start. Container logs (`/var/lib/docker/containers/*/*-json.log`), old images and the journal are the usual space hogs.
- **Out of memory:** `docker inspect` shows `OOMKilled: true`, or the kernel log has `oom` lines. Machine-learning containers and CPU transcodes are the usual culprits.
- **Permissions:** PUID/PGID or volume ownership no longer matches, often after data was moved or a new image changed the user it runs as.
- **Image update:** a `latest` tag pulled a breaking release. Compare the image's creation date with when the breakage started, then read the release notes.
- **Data mount missing:** the data disk didn't mount at boot, so the app writes to or reads an empty directory on the OS disk. Check `findmnt`, and see the mount guards in `../setup/references/storage.md`.
- **Port conflict:** two stacks, or a stack and a host service, are bound to the same port.
- **DNS:** a container can't resolve names, or the LAN's own DNS (AdGuard or Pi-hole) went down and took name resolution with it.
- **Dying drive:** I/O errors in `dmesg`, or SMART reallocated or pending sectors.
- **Address changed:** the server got a new DHCP lease, or its Tailscale node key expired.
- **Power or heat:** throttling, undervoltage on a Pi (`vcgencmd get_throttled`), or a laptop that went to sleep.
- **Expired TLS certificate** on a reverse proxy.
