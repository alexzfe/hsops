# Installing the OS

For a machine with no OS yet. The user does the physical steps at the server. Claude does the parts on the workstation and guides the rest.

## 1. Choose a distro

In a Discovery round (conventions), cover how much the user wants to tinker, how long they want each release to last, and how new the hardware is. Then discuss the options:

| Distro | Fits when |
|---|---|
| Debian stable | They want stability and minimal upkeep. Each release lasts years. The kernel is older, so very new hardware may need backports. |
| Ubuntu Server LTS | They want newer kernels and drivers on recent hardware, 5 years of support, and the most guides online. Ubuntu pushes snaps by default. |
| Fedora Server | They want the newest kernel and packages and don't mind a major upgrade about once a year. |
| Arch | They're experienced, want a rolling release, and want to build it themselves. |
| Raspberry Pi OS Lite (64-bit) | It's a Raspberry Pi. |

Always pick the server or minimal edition, with no desktop, even on a laptop.

## 2. Get the image

Download the image from the distro's official site and check it against the published checksum: `sha256sum -c` with the distro's `SHA256SUMS`, plus the signature where one is published.

On a Raspberry Pi, use Raspberry Pi Imager instead of steps 2 and 3. Its OS customisation settings preconfigure the hostname, user, SSH key and Wi-Fi, so the first boot is already headless.

## 3. Make the USB stick

Offer two ways:

- **A graphical tool:** Ventoy, balenaEtcher or Fedora Media Writer.
- **Claude writes it**, following fixed rule 5:
  1. Run `lsblk -dno NAME,SIZE,MODEL,TRAN` with the stick unplugged, then again after the user plugs it in. The stick is the device that appeared.
  2. Show the user the whole-disk device (`/dev/sdX`, not a partition), its model and its size. Wait for an explicit yes.
  3. Unmount any of its partitions that are mounted.
  4. Write the image: `sudo dd if=<iso> of=/dev/sdX bs=4M status=progress conv=fsync`.
  5. Verify the copy: `sudo cmp -n "$(stat -c%s <iso>)" <iso> /dev/sdX`.

## 4. Firmware (BIOS/UEFI)

Tell the user the boot-menu key. It's usually F12, F11, F7, Esc or Del, depending on the vendor. While they're in the firmware settings, have them apply the power-loss setting from `hardware.md`. Secure Boot can stay on for Debian, Ubuntu and Fedora. Arch needs it off unless they set up signing.

## 5. Installer choices

These choices save work later:

- **Hostname:** this becomes the server's name in hsops.
- **Users:** create an admin user with sudo. On Debian, leaving the root password empty gives the first user sudo.
- **Target disk:** install to the SSD. Confirm the target disk by its size and model, because the installer will erase it. Leave data disks untouched.
- **Software:** no desktop environment. Make sure the SSH server is installed:
  - Debian: in the software selection, tick "SSH server" and "standard system utilities" only.
  - Ubuntu Server: tick "Install OpenSSH server". It can also import the user's SSH key from GitHub.
  - Fedora Server: sshd is enabled by default.
  - Arch: install `openssh` and enable `sshd`.
- **Network:** use a wired connection if at all possible.

## 6. First boot

The user logs in at the console and runs `hostname -I`, then reports the IP. From the workstation, Claude connects with `ssh <user>@<ip>`, using the password this once.

**Done when:** Claude runs a command on the server over SSH. Return to setup phase 0, step 3.
