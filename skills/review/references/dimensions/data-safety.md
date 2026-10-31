# Data safety

Will the user's data survive a dead disk, a deleted folder, ransomware, or a fire?

- **Coverage:** every irreplaceable item in the Services table has a local copy and an off-site copy. Name each item that has fewer.
- **Freshness:** the newest backup of each item, and whether a heartbeat would notice it going stale.
- **Restore:** the date of the last test restore, from the profile. A backup that has never been restored from is unproven.
- **Consistency:** databases are backed up as dumps, not as live data folders.
- **Encryption and keys:** off-site copies are encrypted, and the key exists outside the server.
- **Storage integrity:**
  - SMART: reallocated, pending and uncorrectable sector counts, compared with the baseline
  - pool health
  - when the last scrub ran (ZFS, Btrfs) or the last sync and scrub (SnapRAID).
- **Single copies:** irreplaceable data on one disk with no redundancy and no backup is a **Fix now** finding.
- **Mount safety:** there's a guard against apps writing into an unmounted mountpoint (see `setup/references/storage.md`).
