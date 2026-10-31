# Networking

Can every device reach every service reliably, by name?

- **Address stability:** the server's LAN IP is static or reserved through DHCP. If unclear, ask.
- **DNS:**
  - whether names resolve the same way on the LAN and on the tailnet (MagicDNS, split DNS, local records)
  - whether containers resolve external names
  - a fallback when the server's own DNS is down.
- **Reverse proxy, if any:** certificates are valid and renew automatically, and every route points at a running service.
- **Tailscale:**
  - node key expiry is disabled for the server (otherwise it drops off the tailnet)
  - connections are direct rather than relayed
  - subnet routes or exit node, if used.
- **Docker networks:** stacks reach their databases over internal networks; databases aren't published on host ports without need.
- **Link:** Ethernet speed and duplex; Wi-Fi signal and power saving.
