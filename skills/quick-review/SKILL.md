---
name: quick-review
description: Take a fast look at a homeserver's current health and exposure in one pass, with no agents. Use when the user asks for a quick review, a quick check, or whether anything is wrong with their server.
---

# Quick review

What can hurt the user now, and did anything change for the worse since the last review? One pass in this session, with no agents. Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context, including the newest file in `servers/<server>/reviews/` and the `changelog.md` lines since its date. Use the Priorities in the profile, asking only if none are saved.

## 1. Snapshot

Collect `../review/references/snapshot.md` in one SSH call, without the compose file contents and without "Over time". Mask every secret value. Keep it in this session rather than writing a file.

## 2. Checks

Answer each check from the snapshot, plus any command named here. A check that needs more goes under "Not checked"; don't dig further.

- **Recent changes:** each changelog line since the last review is still in place, and the service it touched is healthy.
- **Done items:** each item marked `done` in the last review still passes its evidence command.
- **Disks:**
  - SMART health, and reallocated, pending and uncorrectable counts
  - pool health
  - any filesystem above 85% of its space or inodes
  - every data mount in the profile is mounted.
- **Backups:** the age of the newest backup of each item in the profile, using the backup tool the profile names. Stale or missing is **Fix now**.
- **Services:**
  - `systemctl --failed`
  - containers stopped, restarting, unhealthy or OOM-killed
  - this boot's journal errors.
- **Exposure:**
  - listening ports compared with the profile; anything public without TLS and authentication is **Fix now** (fixed rule 4)
  - SSH allows passwords or root login
  - the firewall is off
  - pending security updates
  - `.env` files not at mode 600: `find <stacks path> -name '.env*' ! -perm 600`.
- **Heat:** temperatures and throttling, from `sensors`.
- **Profile drift:** services, ports, disks and mounts that differ from the profile.

Tuning, power, image age, config history, DNS design and the rebuild test are left to the `review` skill.

## 3. Report and save

Report only real problems, in this shape:

```
## Quick review: <server> (<date>)
### Fix now
### Recommended
### Regressed     done items that no longer pass
### Not checked   checks skipped, and "dimensions not covered: run /hsops:review"
```

Write each finding as: **title**, evidence, the suggested change, which skill carries it out, and effort (S, M or L). When nothing is wrong, say so in a line. When a finding needs a closer look, name the dimension to run with `review`.

Append the report to the newest file in `reviews/` under a dated `## Quick review` heading, because `fix` and the next review read only that file. New findings continue its numbering and are marked `open`. Regressed items become `failed: <check that failed>`. Leave every other status alone. With no review file yet, start `reviews/YYYY-MM-DD.md`.

**Done when:** the report has been presented and saved.
