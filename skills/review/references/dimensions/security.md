# Security

Who can reach what, and what happens if they do?

- **Exposure:**
  - Map every listening port (`ss -tlnpu`) to a service and to how far it reaches: localhost, LAN, tailnet or public.
  - From the workstation, test what's reachable from the LAN.
  - Anything public without TLS and authentication is **Fix now** (fixed rule 4).
  - Router port forwards are the user's to report; ask.
- **SSH:** key-only login, no root login, and whether fail2ban or a similar tool is worth having given the exposure.
- **Firewall:** whether one is active and whether it matches the exposure the user intends. Docker's published ports bypass ufw; check for that.
- **Updates:** pending security updates, whether automatic security updates are on, and how old the kernel is relative to the running one.
- **Containers:**
  - `privileged: true`, mounts of `/var/run/docker.sock`, `network_mode: host` and extra capabilities. Each needs a reason.
  - Images with no upstream release in a long time.
- **Secrets:** `.env` files are mode 600, and there are no secrets in compose files committed to git.
- **Accounts:** members of the docker and sudo groups, and SSH keys in `authorized_keys` that nobody recognises.
