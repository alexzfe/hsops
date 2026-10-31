---
name: setup
description: Set up a homeserver from wherever the user is starting (bare hardware with no OS, a fresh Linux install, or an existing server to onboard), covering OS install, hardware checks, SSH, remote access, Docker, storage and choosing apps. Use when the user wants to set up, build or start a homeserver, turn a mini PC, laptop, Raspberry Pi or old desktop into a server, or when no hsops server profile exists yet.
---

# Setup

Bootstraps one server and leaves behind its profile. Read `../../shared/conventions.md` (relative to this skill's directory) first; its fixed rules govern every change below.

Work phase by phase; each ends on its **done when**. On an existing server, run each phase as a survey: record what's already there and adopt it, and change only what the user asks for.

Setup records **facts**, each with its evidence (see the evidence rule in the conventions). When something looks wrong, record what was observed, such as "/data has no `nofail` in fstab". Don't call it a problem and don't suggest a fix: judging it is the job of `review`.

## Phase 0: Starting point

1. If `~/.config/hsops/user.md` is missing, ask the user's experience level, how much explanation they want and how much Claude may change without asking (the change level in the conventions), then create it from `../../shared/user-template.md`. On first creation of `~/.config/hsops/`, offer `git init` (and a private remote) for it.
2. Ask where the user is starting from:
   - **Bare hardware** (no OS yet): follow `references/install-os.md`, then return here at phase 1.
   - **Fresh OS:** continue below.
   - **Existing server:** continue below, in survey mode.
3. Create `servers/<name>/` from `../../shared/profile-template.md`, plus empty `lessons.md` and `changelog.md`. Set `access:`; Claude normally runs on the user's workstation, so this is usually `ssh <alias>`.

**Done when:** `user.md` and the server folder exist, and Claude can run a command on the server (over SSH, even with a password, or locally).

## Phase 1: Hardware and OS

Gather everything in one batch:

- `cat /etc/os-release; uname -mr`
- `cat /sys/class/dmi/id/{sys_vendor,product_name,chassis_type}; ls /sys/class/power_supply`
- `lscpu; free -h`
- `lsblk -o NAME,SIZE,TYPE,ROTA,FSTYPE,MOUNTPOINTS,MODEL,SERIAL; df -h`
- `lspci | grep -Ei 'vga|3d|display'; ls -l /dev/dri`
- `ip -br addr`

Identify the form factor, then read its section in `references/hardware.md` and apply the checks there.

Then tell the user what the hardware means for them, at the depth `user.md` asks for:

- **Transcoding:** an Intel iGPU, an NVIDIA card, or CPU only.
- **RAM headroom:** for example, Immich's machine learning wants about 4 GB.
- **Disks:** which disk holds the OS, which holds data, and any disk not yet in use.
- **LAN IP:** whether it changes. Recommend a DHCP reservation on the router (the user's step).
- **Shortfalls:** state plainly where the hardware won't meet their goals.

**Done when:** the profile's Hardware, OS and LAN IP sections are filled from command output, the form-factor checks are applied or declined, and the user has the summary.

## Phase 2: SSH

Skip whatever the OS installer already did.

1. Enable the OpenSSH server.
2. Copy the workstation key to the server with `ssh-copy-id`.
3. Add a `Host <alias>` block to the workstation's `~/.ssh/config`.
4. Confirm `ssh <alias> true` succeeds without a password.
5. Offer hardening (`PasswordAuthentication no`, `PermitRootLogin no`) in a drop-in under `/etc/ssh/sshd_config.d/`. Validate with `sudo sshd -t` and follow fixed rule 3.

**Done when:** `ssh <alias> true` passes without a password, and the profile's Access section is filled.

## Phase 3: Remote access (optional)

Ask whether the user needs to reach the server from outside the home. If they do, discuss the options:

- **Tailscale:** the least setup; no router ports to open.
- **Self-hosted WireGuard:** no third party involved, but needs a port forward and more upkeep.
- **None:** LAN only.

For Tailscale, run `tailscale up`; opening the login URL is the user's step.

**Done when:** the chosen method reaches the server from another device, or the user declined. The profile records either.

## Phase 4: Docker

Install Docker Engine and the Compose plugin from the source the distro table names. Adding the admin user to the `docker` group makes that user root-equivalent; say so, and let the user choose. With an NVIDIA GPU, also install nvidia-container-toolkit and confirm `nvidia-smi` runs in a container.

**Done when:** `docker run --rm hello-world` and `docker compose version` both succeed as the admin user.

## Phase 5: Storage

Follow `references/storage.md`. It works out the layout through a conversation about the user's data and their disks.

**Done when:** every data disk is mounted at boot as storage.md describes, and the profile's Disks and Layout sections record it.

## Phase 6: Choose apps

Ask what the user wants the server for. Walk the matching categories in `../add-service/references/catalog.md`, recommend an app per category based on their needs and hardware, and agree on an order.

**Done when:** the user has confirmed the apps and the order.

## Phase 7: Deploy

Deploy each app with the `add-service` skill, one at a time, verifying each before starting the next.

**Done when:** every chosen app meets add-service's done-when.

Finish with a summary of what's running and how to reach it. If any app holds irreplaceable data, recommend `backups` next; otherwise recommend `monitoring`.
