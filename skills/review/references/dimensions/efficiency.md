# Efficiency

What resources is the server wasting? Power, RAM, disk space and money.

- **Idle power:**
  - the CPU frequency governor and its C-states (`powertop` if installed)
  - a discrete GPU that nothing uses
  - disks that never spin down (`hdparm -C`) and whether that's acceptable
  - the yearly cost at the user's electricity price.
- **RAM:** containers sized well beyond what they use, and services that are installed but idle. Weigh the gains against the user's priorities.
- **Disk space:**
  - unused images and build cache (`docker system df`)
  - container logs with no size limit (set `max-size` in `daemon.json`)
  - the journal's size
  - duplicate media.
- **Redundant services:** two apps doing one job.
- **Tradeoffs:** spinning disks down and lowering power states can hurt Performance. Mark such findings as possible conflicts for the merge step.
