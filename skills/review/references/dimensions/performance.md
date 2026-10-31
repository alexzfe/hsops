# Performance

Where is the server slower than its hardware allows? Every finding names the bottleneck and the measurement that shows it.

- **CPU:** sustained high load, and which container causes it.
- **Transcoding:** whether it uses the available GPU (see the app files' Review checks). Software transcoding on hardware that has a GPU is a common, large win.
- **Memory pressure:** swap activity (`si` and `so` in vmstat), and page cache squeezed out.
- **Disk I/O:**
  - `%util` and await from iostat
  - databases and app caches on HDDs or USB disks when an SSD is available
  - SnapRAID syncs or scrubs running during busy hours.
- **Network:** link speed (`ethtool`, or `cat /sys/class/net/*/speed`), Wi-Fi in place of Ethernet, and Tailscale relaying through DERP instead of connecting directly (`tailscale status`).
- **App settings:** each installed app's Review checks that relate to performance.

Readings from a short sample only get the "snapshot only" label, and come with a suggestion to repeat the review once monitoring has history.
