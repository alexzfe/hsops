---
server: <name>
access: ssh <alias> | local
change-level: <optional; read-only | ask first | normal; overrides user.md for this server>
guard: <optional; off turns the guard hook off for this server>
updated: YYYY-MM-DD
---

# <name>

## Priorities
<what the user cares about most, in order, e.g. data safety > low upkeep > power draw; plus constraints such as budget or no downtime in the evenings>

## Hardware
- Form factor: <laptop | mini PC | desktop | Raspberry Pi | other>
- CPU / cores / arch:
- RAM:
- GPU / transcoding: <Intel iGPU (/dev/dri) | NVIDIA <model> | none>
- Disks: <device, size, SSD/HDD, serial, mount, role: os | data | media | backup>

## OS
- Distro / version:
- Admin user:

## Access
- LAN IP: <ip; DHCP reservation yes/no>
- SSH: <port; key auth; password auth off?>
- Remote access: <Tailscale name | WireGuard | none>

## Layout
- Stacks: <where compose projects live, discovered or chosen>
- App data: <path>
- Media / bulk storage: <paths, and the storage layout chosen>

## Services
| app | stack path | port | reached via | data to back up | backed up? |
|-----|------------|------|-------------|-----------------|------------|

## Monitoring
<what is checked, by which tool, where alerts go>

## Backups
<tool; what goes where; schedule; date of the last test restore>
