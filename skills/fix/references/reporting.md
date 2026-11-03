# Reporting a fix batch

Templates for what the user sees while `fix` runs. They report the batch; they never repeat plan details. Fill them from the review file's statuses, not from memory.

## Approval summary

Opens the approval brief, before the full plans. One row per fix:

```
| Fix | Items | What changes for you | Disruption | You do |
| 1 | R14 (check the nightly backup ran) | ConfigBackupStale alerts if the 03:30 push stops | none | nothing |
| 2 | R13, R14 | node-exporter reports mounts and timers | ~30 s gap in host metrics | nothing |
```

"What changes for you" is what the user will see or notice afterwards: a new alert, a Discord message, a gap in a service, a job that now runs weekly. Write "nothing visible" when that is true.

## Progress board

```
**Progress:** Run, fix 2 of 5
| Item | What it is | Fix | Status |
| R13 | Alert when a disk mount disappears | 2, 4 | ✅ done |
| R14 | Check the nightly backup and push ran | 2, 3 | ▶ running |
| N7 | Confirm alerts reach Discord | 4 | ⏳ approved |
Next: recreate node-exporter (~30 s gap in host metrics)
```

- One row per item, not per fix. The Fix column maps items to plans when one plan covers several items or one item spans several plans.
- An item is ✅ done, and marked `done` in the review file, only once every fix in its Fix column has passed.
- Statuses: ⏳ approved, ▶ running, ✅ done, ❌ failed, ⏸ paused (waiting on the user), ⏳ not run (at Close, after a stop).
- **When:** once after approval; after each fix's checks, under its fix result; whenever the run stops for a failure or a deviation; and as the final record at Close.
- **Skip it** for batches of one or two items. The fix result is enough.

## Fix result

After each fix's checks, whether it passed or failed:

```
**Fix 2 of 5 done: node-exporter reads systemd** (R13, R14)
Changed: <one line: what is different on the server>
For you: <what the user will see or notice, or "nothing visible">
Checked: plan check ✓ · evidence gone ✓ · health matches baseline ✓ · verify agent ✓
Deviations: <none, or each one and the user's decision>
```

On a failure, the heading reads `**Fix 2 of 5 failed: <name>**`, the failed check is marked ✗ with its evidence below, and the plan's rollback follows.
