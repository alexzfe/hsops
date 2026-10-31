---
name: backups
description: Set up, check or restore homeserver backups, covering what to back up, local and off-site copies, database dumps, scheduling, heartbeats and test restores. Use when the user wants backups, asks whether their data is safe, needs to restore something, or after deploying an app that holds irreplaceable data.
---

# Backups

Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context. Restoring follows steps 1 and 8. Setting up follows all of them.

1. **Inventory.** List what needs backing up:
   - the "data to back up" column of the Services table
   - the stack folders: compose files and `.env` files. `.env` files hold secrets, so the backup must be encrypted.
   - anything else the user names.
   
   Mark each item irreplaceable or replaceable. Replaceable media is the user's call.
2. **Needs.** Ask about:
   - the data size and their upload bandwidth (estimate how long the first off-site upload will take)
   - their budget for off-site storage
   - where an off-site copy could live: cloud object storage, a friend's server, a second box on the tailnet
   - the retention they want
   - whether they prefer a CLI or a UI.
3. **Choose a tool** that fits those answers:

   | Tool | Strengths | Costs |
   |---|---|---|
   | restic (optionally the Backrest UI) | Encrypted and deduplicated; one binary; many backends. | CLI-first. |
   | BorgBackup + borgmatic | Encrypted and deduplicated; very efficient. | The target needs borg installed (or BorgBase). |
   | Kopia | Encrypted and deduplicated, with a built-in UI. | Smaller community. |
   | ZFS send/receive | Snapshot-exact, very fast incrementals. | Needs ZFS on both ends. |
   | rclone or rsync + snapshots | Simple, plain files. | No dedup; encryption only with rclone crypt. |

4. **Targets.** One local copy (another disk or machine) and one off-site copy. Off-site copies must be encrypted. The encryption key or password must also be stored *outside* the server, for example in a password manager: losing it makes every backup unreadable. Say this explicitly.
5. **Consistency.** Never copy a live database's data folder. Dump it first (`pg_dump` or `mysqldump` inside its container, or the app's own dumps), or stop the app briefly, and back up the dump.
6. **Schedule.** Use a systemd timer, or the tool's own scheduler, with the retention the user chose.
7. **Heartbeat.** Each successful run pings a push monitor, so the user is alerted when a backup *doesn't* happen (see `monitoring`).
8. **Test restore.** Restore some files and a database dump into a scratch folder:
   - Compare the restored files' checksums with the originals.
   - Load the database dump into a throwaway container and query it.
9. **Record.** Fill in the profile's Backups section (tool, what goes where, schedule, test restore date) and its "backed up?" column, and add a line to `changelog.md`.

**Done when:** every irreplaceable item has a local copy and an off-site copy, the first backup has completed, a withheld heartbeat has raised an alert, and a test restore has succeeded, with the date recorded.
