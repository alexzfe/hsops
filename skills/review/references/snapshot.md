# Snapshot

One pass of read-only facts that every dimension reviewer starts from. Collect each section. If a command or tool is missing, record that section as unavailable rather than installing anything.

## Host
- `cat /etc/os-release; uname -mr; uptime; systemctl is-system-running; systemctl --failed`
- `lscpu | head -20; free -h; swapon --show`
- `cat /sys/class/dmi/id/{sys_vendor,product_name,chassis_type}`
- `sensors` (if installed)

## Storage
- `lsblk -o NAME,SIZE,TYPE,ROTA,FSTYPE,MOUNTPOINTS,MODEL,SERIAL; df -h; df -i; findmnt --fstab`
- `cat /etc/fstab`
- `sudo -n smartctl --scan`, then `sudo -n smartctl -H -A` for each disk
- Pool health where the layout uses one: `zpool status`, `btrfs device stats`, `snapraid status`, `cat /proc/mdstat`

## Docker
- `docker version --format '{{.Server.Version}}'; docker system df`
- `docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'`
- every compose file in the stacks layout, with `.env` values masked
- `docker inspect` restart policy, health, `OOMKilled`, mounts, privileged and capabilities for each container
- the log driver and log sizes: `sudo -n du -sh /var/lib/docker/containers/*/*-json.log`

## Network and access
- `ip -br addr; ip route; resolvectl status 2>/dev/null | head -30`
- `ss -tlnpu`
- the effective sshd settings: `sudo -n sshd -T | grep -Ei 'passwordauth|permitroot|port|pubkey'`
- the firewall state: `ufw status verbose`, `firewall-cmd --list-all` or `nft list ruleset`
- `tailscale status` (if installed)

## Updates and maintenance
- pending updates (`apt list --upgradable`, `dnf check-update` or `checkupdates`), and whether automatic security updates are on
- `journalctl --disk-usage`; `journalctl -p err -b --no-pager | tail -50`

## Over time

Find history first: a running Netdata, Prometheus or Beszel, or `sar` from sysstat. If there's history, pull the last 7 days of CPU, memory, disk I/O and network.

If there's none, sample for about 5 minutes while the other sections run: `vmstat 5 60`, plus `iostat -x 5 60` if sysstat is installed, and `docker stats --no-stream` every 30 seconds. Label every finding based on this sample "snapshot only".
