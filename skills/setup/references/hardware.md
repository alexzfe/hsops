# Hardware by form factor

Identify the form factor from `chassis_type`, a battery under `/sys/class/power_supply`, and the vendor and product name. Common `chassis_type` values: 3 or 4 desktop, 8–10 or 14 laptop, 35 or 36 mini PC. Apply the section that matches, at the depth `user.md` asks for.

## Laptop

- **Lid:** create a drop-in `/etc/systemd/logind.conf.d/lid.conf` setting `HandleLidSwitch=ignore`, `HandleLidSwitchExternalPower=ignore` and `HandleLidSwitchDocked=ignore`, then restart `systemd-logind`. This may end the console session, so it counts as disruptive.
- **Sleep:** `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`.
- **Battery:**
  - A battery charging around the clock wears out and can swell. If `/sys/class/power_supply/BAT*/charge_control_end_threshold` exists, set a limit (60–80%) and make it persist with a systemd unit or TLP.
  - If there's no threshold, discuss the alternatives: removing the battery if that's possible, or keeping an eye on it for swelling.
  - Upside: the battery works as a small UPS.
- **Screen:** blank the console with the `consoleblank=60` kernel parameter.
- **Network:** Ethernet is much more reliable; a USB adapter is fine. If Wi-Fi is the only option, turn off Wi-Fi power saving.
- **Heat:** a laptop in a closed cupboard overheats. Check temperatures under load with `sensors`.

## Mini PC

- **Power loss:** set the firmware option that powers the machine on when power returns. Vendors name it "Restore on AC Power Loss", "AC Back" or "State after G3".
- **iGPU:** most Intel mini PCs (N100, N150, N305, Core) have QuickSync, which handles transcoding well. Check that `/dev/dri/renderD128` exists. Very new chips may need a newer kernel or firmware, which favors Ubuntu or Fedora.
- **Storage:** usually one NVMe slot and maybe one 2.5" bay, so bulk storage often goes in USB enclosures. Use enclosures with UAS, mount the disks by UUID with `nofail`, and expect the occasional disconnect. Point this out when choosing a storage layout: ZFS over USB is fragile.
- **Fanless units** throttle under sustained load. Check temperatures during a transcode.

## Desktop or tower

- **Power draw:** an older desktop often idles at 30–60 W, against 6–15 W for a mini PC. Work out the yearly cost with the user's electricity price. It matters for a machine that never turns off.
- **Room to grow:** count the drive bays and SATA ports; they decide which storage layouts are possible.
- **Discrete GPU:** it adds idle draw. Keep it only if it's used for transcoding or machine learning.
- **Power loss:** same firmware setting as on a mini PC.

## Raspberry Pi or other ARM board

- **Architecture:** it's arm64, so check every app image for an arm64 build (`add-service` does this check).
- **Boot drive:** boot from an SSD (USB, or an NVMe HAT on a Pi 5) rather than the SD card. Database writes wear SD cards out.
- **Power:** use the official power supply. `vcgencmd get_throttled` reporting anything other than `0x0` means undervoltage or throttling.
- **Transcoding:** the Pi 5 has no hardware video encoder, so media servers should rely on direct play.
- **RAM:** a 4 GB model is tight for Immich's machine learning or several databases at once.
