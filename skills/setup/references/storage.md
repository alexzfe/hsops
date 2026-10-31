# Storage

## Choosing a layout

Ask the user about:

- **Their data:** irreplaceable (photos, documents) or replaceable (media they could download again).
- **Disks:** how many now, how many later, and whether they're the same size.
- **RAM.**
- **Growth:** whether they want to add one disk at a time.
- **Complexity:** how much they're willing to take on.

Then discuss the layouts that fit:

| Layout | Strengths | Costs |
|---|---|---|
| Single disk, ext4 or XFS | Simplest; any tool can recover it. | No redundancy; a dead disk means restoring from backup. |
| mergerfs + SnapRAID | Mixed disk sizes, add a disk at a time, the remaining disks stay readable if one fails, idle disks can spin down. | Parity only updates when the sync runs (a schedule). Best for media that rarely changes. |
| ZFS mirror or RAIDZ | Checksums and self-healing, snapshots, `zfs send` for backups. | Wants same-size disks and plenty of RAM. Growing a pool is less flexible. Not a module in mainline Linux. |
| Btrfs raid1 | Checksums and snapshots, built into the kernel, mixed sizes work. | Its RAID5/6 is still not trusted. Tooling is less mature than ZFS. |
| mdadm RAID1 + ext4 | Mature, simple mirroring. | No checksums. Same-size disks. |

Always say it plainly: **RAID protects against a dead disk, not against deleted, corrupted or encrypted files.** Irreplaceable data also needs the `backups` skill.

## Mounting

- Add each data disk to fstab by `UUID=`, with `nofail,x-systemd.device-timeout=10s` so a missing disk doesn't stop the boot.
- **Apps must never write into an unmounted mountpoint.** If the disk didn't mount, Docker happily writes to the empty folder on the OS disk instead. Guard against it with `sudo chattr +i <mountpoint>` while the disk is unmounted, or by adding `RequiresMountsFor=<path>` to `docker.service` in a drop-in.
- Set ownership to match the user IDs the app containers run as.
- Record a SMART baseline for each disk with `smartctl -a`.

## Adding a disk

1. Identify the disk the way fixed rule 5 requires: `lsblk` before and after it's connected, with its serial recorded.
2. Check its health with `smartctl -H` and `-a`. For a used disk, read the reallocated and pending sector counts.
3. Look for existing data with `lsblk -f` and `blkid`. Formatting destroys it, so get a go-ahead that names the device, its model and its serial.
4. Format it or add it to the pool, following the layout already chosen.
5. Add it to fstab as described above, then run `sudo mount -a` and check with `findmnt`.
6. Update the profile's Disks section and add a line to `changelog.md`.

**Done when:** `findmnt` shows the disk at its mountpoint after `mount -a` (or after a reboot, if the user agrees to one), and the profile is updated.
