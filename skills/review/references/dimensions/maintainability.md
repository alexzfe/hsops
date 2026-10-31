# Maintainability

Could the user, or a future session, understand, update and rebuild this server?

- **Image tags:** `latest` on apps that break between releases; images far behind upstream; whether updates are deliberate or handled by an auto-updater such as Watchtower (risky for apps with breaking releases).
- **Compose hygiene:** one folder per stack, secrets in `.env`, hard-coded values that should be variables, stacks that are no longer used.
- **Config history:** whether the stack folders are in git (with `.env` ignored).
- **Profile drift:** compare the profile with reality, covering services, ports, disks and mounts. List every difference.
- **Rebuild test:** if the OS disk died today, could the server be rebuilt from the backups plus the profile? Name what's missing.
- **OS age:** how close the distro release is to its end of life.
