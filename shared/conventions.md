# hsops conventions

Shared reference for every hsops skill and the `reviewer` agent.

## Data folder

Everything hsops knows about the user and their servers lives in `~/.config/hsops/`, outside the plugin:

- `user.md`: the user's experience level and preferences, which hold across all servers (shape: `shared/user-template.md`).
- `general/<skill>.md`: general lessons this user's sessions taught, one file per skill.
- `servers/<server>/`, one folder per machine:
  - `profile.md`: facts about the box, plus the user's priorities (shape: `shared/profile-template.md`).
  - `lessons.md`: what this particular server has taught.
  - `changelog.md`: one dated line per change made.
  - `reviews/YYYY-MM-DD.md`: saved reviews, with the status of each recommendation.

Picking the server: one folder → use it. Several → the one the conversation names, else ask. None → run `setup`.

## Load context first

Read these before acting:

- `user.md`
- `general/<this skill>.md`, if it exists
- the server's `profile.md` and `lessons.md`
- the last ~20 lines of the server's `changelog.md`.

Match the depth of explanation to the experience level in `user.md`. When the profile disagrees with what you observe, trust the observation and correct the profile.

## Evidence

Write to the data folder only what has evidence: command output or a file seen in this session, or the user's own words. Anything else, such as an inference or a guess or something that "should be true", gets checked first with a read-only command or asked of the user. If it can't be confirmed, it doesn't get written. Preferences go into `user.md` only when the user has stated or confirmed them. Each line is one short sentence with no hedging. The evidence hook backs this up: the first write to each file in a session is sent back once, asking for the evidence, and so is any write with hedged lines.

## Advising

Ask about needs and priorities before suggesting anything. Then present 2–3 options that fit, with their tradeoffs, and recommend the one that fits what the user said, explaining why. The user's choice is final: build around the tool or layout they pick. On an existing server, **adopt** its layout and naming. Offer the suite's layout only on a blank server.

## Asking for approval

Anything the user must review (diffs, compose files, reports, lists of changes) goes in the message itself, as a brief, before the question. The approval question that follows is short and holds only the choices. Long content never goes inside an interactive question or its preview, because it gets cut off there.

## Running commands

Claude usually runs on the user's workstation. The profile's `access:` field decides how commands reach the server:

- `ssh <alias>`: run as `ssh <alias> '<cmd>'`, batching read-only checks into one call. For multi-line file writes, draft the file in the scratchpad and `scp` it, or pipe a heredoc into `sudo tee`.
- `local`: Claude runs on the server itself; run commands directly.

Root commands use `sudo -n`. When sudo needs a password, hand the exact command to the user to run in their own terminal and ask for the output.

## Change level

How much Claude may change on the server without asking. `user.md` sets the default (`normal` if unset), and a server's `profile.md` can override it with `change-level:`.

- **read-only:** run only commands that read state. Anything that would change the server goes into a "would do" list, with the exact commands, for the user to run.
- **ask first:** ask before every change, small ones included.
- **normal:** make routine changes; disruptive ones follow fixed rule 2.

Fixed rule 2 applies at every level.

## Distros

Debian, Ubuntu, Raspberry Pi OS, Fedora and Arch are supported. On anything else, work out the equivalents from `/etc/os-release`.

| | Debian / Ubuntu / Pi OS | Fedora | Arch |
|---|---|---|---|
| Install | `apt install` | `dnf install` | `pacman -S` |
| Upgrade | `apt update && apt upgrade` | `dnf upgrade` | `pacman -Syu` (rolling release, so upgrade deliberately) |
| Docker | Docker's apt repo (on Ubuntu, not the snap) | Docker's dnf repo | `docker`, `docker-compose` from the distro |
| Firewall | `ufw` or nftables | `firewalld` | nftables or `ufw` |
| Automatic security updates | `unattended-upgrades` | `dnf-automatic` | none; upgrade manually |

## Fixed rules

Every choice above is flexible. These rules are not. A user may override one knowingly for a specific case; record the override in the server's `lessons.md` so later sessions don't re-argue it.

1. Copy a config file to `<file>.bak-YYYYMMDD` before editing it.
2. A **disruptive** change is anything that touches data, access or a running service. It needs the user's go-ahead for that specific change, with the rollback stated. The guard hook backs this up: it asks the user directly before commands that destroy data, and denies other disruptive commands once until you've shown the go-ahead. `guard: off` in a profile turns it off for that server.
3. While changing access settings (sshd, firewall, network, Tailscale), keep the current session open and prove the new state works over a second connection.
4. Anything exposed to the public internet sits behind TLS and authentication. Access over the LAN or a tailnet can go without them.
5. Write only to a block device identified by running `lsblk` before and after it was plugged in, and confirmed by the user by model and size.
6. A backup isn't finished until a test restore has succeeded.
7. An optimization isn't finished until it's been measured before and after.
8. Append every change to `changelog.md` as `YYYY-MM-DD <what> (<why>)`, and update `profile.md` in the same turn when a fact changed.
9. Secrets live only in the server's own files (a stack's `.env` with mode 600, or the backup tool's key file). They never go into the data folder or the suite.

## Closing a task

When a task changed the server, not only the data folder, finish by running the `review-changes` skill, once per task.

When a task hit a **surprise** (a cause that wasn't obvious, a step that failed and the fix, a fact the profile lacked, a preference the user stated), offer `/hsops:learn` in one line.
