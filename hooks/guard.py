#!/usr/bin/env python3
"""hsops guard: a PreToolUse hook on Bash that backs up fixed rules 2, 3 and 5.

- Commands that destroy data permanently get `ask`: the user sees the exact command and decides.
- Other disruptive commands are denied once. The denial makes Claude show the user's go-ahead,
  and the identical command retried within the window then runs once (ECC GateGuard's pattern).
- Codex can't `ask` yet, so there every match is denied once with a retry.

Commands on the server are checked inside `ssh` (including quoted remote commands, `sh -c` and
heredocs). Local commands are checked only for writes to block devices, unless a profile says
`access: local`. A profile with `guard: off` turns the checks off for that server.
"""

import os
import re
import shlex

import _hook

ASK, DENY = "ask", "deny"

DATA_PATHS = ["/srv", "/mnt", "/media", "/data", "/home", "/opt", "/var/lib"]
ACCESS_FILES = [
    "/etc/ssh/", "/etc/fstab", "/etc/crypttab", "/etc/sudoers", "/etc/ufw/", "/etc/nftables",
    "/etc/firewalld/", "/etc/iptables/", "/etc/sysconfig/iptables", "/etc/netplan/",
    "/etc/network/interfaces", "/etc/NetworkManager/system-connections/",
]
HARMLESS_DEVICES = ("/dev/null", "/dev/zero", "/dev/stdout", "/dev/stderr", "/dev/tty", "/dev/fd/")
# Prefix commands, with the short options that take an argument.
WRAPPERS = {"sudo": "ugCDhpUrt", "doas": "uC", "env": "uCS", "nohup": "", "time": "fo", "nice": "n",
            "ionice": "cnp", "stdbuf": "ioe"}
SSH_ARG_OPTS = "bcDEeFIiJLlmOoPpQRSWw"
PUNCT = ";&|<>()\n"


class Finding:
    def __init__(self, tier, what, access=False):
        self.tier, self.what, self.access = tier, what, access


# --- parsing -------------------------------------------------------------------------------

def tokenize(cmd):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=PUNCT)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:  # unbalanced quotes: fall back to a rough split
        return re.findall(r"[;&|\n()]+|[<>]+|[^\s;&|()<>]+", cmd)


def segments(cmd):
    """Split a command line into simple commands; redirections stay inside their command."""
    seg, out = [], []
    for tok in tokenize(cmd):
        if tok and all(c in PUNCT for c in tok) and not any(c in "<>" for c in tok):
            if seg:
                out.append(seg)
            seg = []
        else:
            seg.append(tok)
    if seg:
        out.append(seg)
    return out


def skip_options(args, i, arg_opts):
    """Index of the first non-option at or after i, skipping the arguments of short options."""
    while i < len(args) and args[i].startswith("-") and args[i] != "-":
        opt = args[i]
        i += 1
        if opt == "--":
            break
        if opt.startswith("--"):
            continue
        for j, ch in enumerate(opt[1:]):
            if ch in arg_opts:
                if j == len(opt) - 2:
                    i += 1
                break
    return i


def unwrap(seg):
    """Drop `VAR=x`, sudo, env and similar prefixes so the real command comes first."""
    i = 0
    while i < len(seg):
        word = os.path.basename(seg[i])
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
            i += 1
        elif word in WRAPPERS:
            i = skip_options(seg, i + 1, WRAPPERS[word])
        else:
            break
    return seg[i:]


def ssh_split(args):
    """(host, remote command) for `ssh [options] host [command]`."""
    i = skip_options(args, 1, SSH_ARG_OPTS)
    if i >= len(args):
        return None, ""
    return args[i].split("@")[-1], " ".join(args[i + 1:])


def flags(args):
    """Short flag letters and long options among args."""
    short, long_ = set(), set()
    for a in args:
        if a.startswith("--"):
            long_.add(a.split("=")[0])
        elif a.startswith("-") and len(a) > 1:
            short.update(a[1:])
    return short, long_


def positional(args):
    out, rest = [], False
    for a in args:
        if rest or not a.startswith("-"):
            out.append(a)
        elif a == "--":
            rest = True
    return out


def subcommand(args, known):
    return next((a for a in args if a in known), None)


# --- paths ---------------------------------------------------------------------------------

def norm(path):
    return path.rstrip("/") or "/"


def under(path, roots):
    p = norm(path)
    return any(p == norm(r) or p.startswith(norm(r) + "/") for r in roots)


def is_device(path):
    return path.startswith("/dev/") and not path.startswith(HARMLESS_DEVICES)


def is_access_file(path):
    return any(path.startswith(f) for f in ACCESS_FILES)


def profile_data_paths():
    """Mount points and layout paths the profiles list, added to the fixed data paths."""
    paths = []
    for _, text in _hook.profiles():
        section = None
        for line in text.splitlines():
            if line.startswith("## "):
                section = line[3:].strip()
            if section == "Layout" or line.lstrip("- ").startswith("Disks:"):
                paths += re.findall(r"(?<![\w.])/(?:[\w.-]+/?)+", line)
    return paths


class Context:
    def __init__(self):
        self.data_paths = DATA_PATHS + profile_data_paths()

    def is_data(self, path):
        p = path.replace("$HOME", "~")
        if p in ("~", "~/", "*", "/*", "/") or re.fullmatch(r"/[^/]+/?\*?", p):
            return True  # the filesystem root, a top-level directory, home or everything here
        return under(p.rstrip("*"), self.data_paths)


# --- the checks ----------------------------------------------------------------------------

def check(seg, remote, ctx, depth=0):
    """Findings for one simple command; recurses into commands that run other commands."""
    args = unwrap(seg)
    if not args or depth > 4:
        return []
    cmd, rest = os.path.basename(args[0]), args[1:]
    short, long_ = flags(rest)
    pos = positional(rest)
    found = []

    def nested(text, remote_=remote):
        for s in segments(text):
            found.extend(check(s, remote_, ctx, depth + 1))

    # Commands that run other commands.
    if cmd == "ssh":
        _, remote_cmd = ssh_split(args)
        if remote_cmd:
            nested(remote_cmd, True)
        return found
    if cmd in ("sh", "bash", "zsh", "dash", "ksh", "su") and "-c" in rest:
        i = rest.index("-c")
        if i + 1 < len(rest):
            nested(rest[i + 1])
        return found
    if cmd == "eval" and rest:
        nested(" ".join(rest))
        return found
    if cmd in ("docker", "podman") and "exec" in rest:
        tail = rest[rest.index("exec") + 1:]
        while tail and tail[0].startswith("-"):
            tail = tail[2:] if tail[0] in ("-e", "-u", "-w", "--env", "--user", "--workdir") else tail[1:]
        if len(tail) > 1:
            nested(" ".join(shlex.quote(t) for t in tail[1:]))
        return found
    if cmd == "xargs":
        tail = [a for a in rest if not a.startswith("-")]
        if tail:
            found.extend(check(tail, remote, ctx, depth + 1))
        return found

    # Writes to block devices and pools: checked everywhere, including the workstation.
    if cmd.startswith("mkfs") or cmd in ("mke2fs", "mkswap", "blkdiscard"):
        found.append(Finding(ASK, f"`{cmd}` formats or discards a device"))
    elif cmd == "wipefs" and (short & set("ao") or long_ & {"--all", "--offset"}):
        found.append(Finding(ASK, "`wipefs` erases filesystem signatures"))
    elif cmd == "dd":
        for a in rest:
            if a.startswith("of=") and is_device(a[3:]):
                found.append(Finding(ASK, f"`dd` writes to the device {a[3:]}"))
    elif cmd == "shred" and any(is_device(p) for p in pos):
        found.append(Finding(ASK, "`shred` overwrites a device"))
    elif cmd == "zpool" and subcommand(rest, {"destroy", "labelclear"}):
        found.append(Finding(ASK, f"`zpool {subcommand(rest, {'destroy', 'labelclear'})}` destroys a pool"))
    elif cmd == "zfs" and "destroy" in rest:
        found.append(Finding(ASK, "`zfs destroy` deletes a dataset or snapshot"))
    elif cmd == "sgdisk" and (short & set("Zo") or long_ & {"--zap", "--zap-all", "--clear"}):
        found.append(Finding(ASK, "`sgdisk` wipes a partition table"))
    elif cmd == "sfdisk" and not (short & set("ldV") or long_ & {"--list", "--dump", "--verify", "--json"}):
        found.append(Finding(ASK, "`sfdisk` rewrites a partition table"))
    elif cmd == "parted" and subcommand(rest, {"mklabel", "mkpart", "rm", "resizepart"}):
        found.append(Finding(ASK, "`parted` changes a partition table"))
    elif cmd == "cryptsetup" and subcommand(rest, {"luksFormat", "erase", "luksErase"}):
        found.append(Finding(ASK, "`cryptsetup` formats or erases an encrypted device"))
    elif cmd == "mdadm" and long_ & {"--create", "--zero-superblock"}:
        found.append(Finding(ASK, "`mdadm` creates an array or erases a superblock"))
    elif cmd in ("pvremove", "vgremove", "lvremove"):
        found.append(Finding(ASK, f"`{cmd}` deletes LVM storage"))
    if found or not remote:
        return found

    # On the server: data loss, interrupted services and access changes.
    if cmd == "rm" and (short & set("rR") or "--recursive" in long_):
        targets = [p for p in pos if ctx.is_data(p)]
        if targets:
            found.append(Finding(ASK, f"`rm -r` deletes {', '.join(targets)}"))
    elif cmd == "find" and ("-delete" in rest or ("-exec" in rest and "rm" in rest)):
        starts = [a for a in rest[:next((i for i, a in enumerate(rest) if a[:1] in "-(!"), len(rest))]]
        if any(ctx.is_data(s) for s in starts):
            found.append(Finding(ASK, f"`find` deletes files under {', '.join(starts)}"))
    elif cmd in ("docker", "podman", "docker-compose"):
        found.extend(check_docker(cmd, rest))
    elif cmd == "systemctl":
        sub = subcommand(rest, {"stop", "restart", "disable", "mask", "kill", "isolate", "try-restart",
                                "reload-or-restart", "reboot", "poweroff", "halt", "kexec", "rescue", "emergency"})
        if sub:
            units = [p for p in pos if p != sub]
            found.append(Finding(DENY, f"`systemctl {sub}` {' '.join(units)}".rstrip(),
                                 access=any(u.startswith(("ssh", "tailscale", "ufw", "firewalld", "nftables", "NetworkManager", "systemd-networkd")) for u in units)))
    elif cmd == "service" and len(pos) >= 2 and pos[1] in ("stop", "restart"):
        found.append(Finding(DENY, f"`service {pos[0]} {pos[1]}`", access=pos[0].startswith("ssh")))
    elif cmd in ("reboot", "shutdown", "poweroff", "halt") or (cmd == "init" and pos[:1] in (["0"], ["6"])):
        found.append(Finding(DENY, f"`{cmd}` takes the server down"))
    elif cmd in ("apt", "apt-get") and subcommand(rest, {"remove", "purge", "autoremove", "autopurge"}):
        found.append(Finding(DENY, f"`{cmd} {subcommand(rest, {'remove', 'purge', 'autoremove', 'autopurge'})}` removes packages"))
    elif cmd in ("dnf", "yum", "microdnf", "zypper") and subcommand(rest, {"remove", "erase", "autoremove", "rm"}):
        found.append(Finding(DENY, f"`{cmd}` removes packages"))
    elif (cmd == "pacman" and any(a.startswith("-R") for a in rest)) or (cmd == "snap" and "remove" in rest) \
            or (cmd == "apk" and "del" in rest):
        found.append(Finding(DENY, f"`{cmd}` removes packages"))
    elif cmd in ("chown", "chmod") and (short & {"R"} or "--recursive" in long_):
        targets = [p for p in pos[1:] if ctx.is_data(p)]
        if targets:
            found.append(Finding(DENY, f"`{cmd} -R` on {', '.join(targets)}"))
    elif cmd == "umount":
        found.append(Finding(DENY, f"`umount` {' '.join(pos)}".rstrip()))
    elif cmd == "crontab" and "r" in short:
        found.append(Finding(DENY, "`crontab -r` deletes the crontab"))
    elif cmd in ("pkill", "killall"):
        found.append(Finding(DENY, f"`{cmd}` stops processes"))
    elif cmd == "btrfs" and "subvolume" in rest and "delete" in rest:
        found.append(Finding(ASK, "`btrfs subvolume delete` deletes a subvolume"))
    elif cmd in ("rsync", "scp"):
        found.extend(check_copy(cmd, rest, long_))
    else:
        found.extend(check_access(cmd, rest, short, long_, pos))
    found.extend(check_access_file_write(cmd, args, short, long_))
    return found


COMPOSE_SUBS = {"down", "rm", "stop", "kill", "up", "ps", "logs", "pull", "restart", "exec", "config", "start"}


def check_docker(cmd, rest):
    if cmd == "docker-compose" or "compose" in rest:
        tail = rest[rest.index("compose") + 1:] if "compose" in rest else rest
        sub = subcommand(tail, COMPOSE_SUBS)
        short, long_ = flags(tail)
        if sub == "down" and ("v" in short or "--volumes" in long_):
            return [Finding(ASK, "`docker compose down -v` deletes the stack's volumes")]
        if sub in ("down", "rm", "stop", "kill", "restart"):
            return [Finding(DENY, f"`docker compose {sub}` stops or removes the stack's containers")]
        return []
    short, long_ = flags(rest)
    words = [a for a in rest if not a.startswith("-")]
    if words[:2] in (["volume", "rm"], ["volume", "prune"], ["volume", "remove"]):
        return [Finding(ASK, f"`docker volume {words[1]}` deletes volumes")]
    if words[:2] == ["system", "prune"]:
        if "--volumes" in long_:
            return [Finding(ASK, "`docker system prune --volumes` deletes unused volumes")]
        return [Finding(DENY, "`docker system prune` removes stopped containers, networks and images")]
    if words[:1] in (["rm"], ["stop"], ["kill"]) or (words[:1] == ["container"] and words[1:2] in (["rm"], ["stop"], ["kill"], ["prune"])) \
            or words[:2] in (["image", "prune"], ["network", "prune"]):
        return [Finding(DENY, f"`{cmd} {' '.join(words[:2])}` stops or removes containers or data")]
    return []


def check_copy(cmd, rest, long_):
    found = []
    dests = [a.split(":", 1)[1] for a in positional(rest)[-1:] if re.match(r"^[\w.@-]+:", a)]
    for d in dests:
        if is_access_file(d):
            found.append(Finding(DENY, f"`{cmd}` overwrites {d}", access=True))
    if cmd == "rsync" and dests and any(o.startswith("--delete") for o in long_):
        found.append(Finding(DENY, "`rsync --delete` removes files on the server"))
    return found


def check_access(cmd, rest, short, long_, pos):
    reads = {
        "ufw": lambda: not pos or pos[0] in ("status", "show", "version", "app") or "--dry-run" in long_,
        "nft": lambda: (pos[:1] in (["list"], ["monitor"])) or "c" in short or "--check" in long_,
        "firewall-cmd": lambda: all(a.startswith(("--list", "--get", "--query", "--info", "--state", "--help", "--zone")) for a in rest),
    }
    if cmd in reads:
        return [] if reads[cmd]() else [Finding(DENY, f"`{cmd}` changes the firewall", access=True)]
    if re.fullmatch(r"ip6?tables(-nft|-legacy)?", cmd):
        if short & set("AIDRFXPNEZ") or long_ & {"--append", "--insert", "--delete", "--replace", "--flush",
                                                 "--delete-chain", "--policy", "--new-chain", "--zero"}:
            return [Finding(DENY, f"`{cmd}` changes the firewall", access=True)]
    if re.fullmatch(r"ip6?tables(-nft|-legacy)?-restore|nft-restore", cmd):
        return [Finding(DENY, f"`{cmd}` replaces the firewall rules", access=True)]
    if cmd == "tailscale" and pos[:1] in (["down"], ["logout"], ["up"], ["set"]):
        return [Finding(DENY, f"`tailscale {pos[0]}` changes remote access", access=True)]
    if cmd == "wg-quick" and pos[:1] == ["down"]:
        return [Finding(DENY, "`wg-quick down` stops a VPN tunnel", access=True)]
    if cmd == "ip" and (("link" in pos and "down" in pos) or (pos[:1] in (["addr"], ["address"], ["route"]) and set(pos) & {"del", "flush", "replace"})):
        return [Finding(DENY, "`ip` changes the network", access=True)]
    if cmd == "nmcli" and set(pos) & {"down", "delete", "modify", "off", "disconnect"}:
        return [Finding(DENY, "`nmcli` changes the network", access=True)]
    if cmd == "netplan" and pos[:1] == ["apply"]:
        return [Finding(DENY, "`netplan apply` changes the network", access=True)]
    return []


def check_access_file_write(cmd, args, short, long_):
    """Writes to sshd, firewall, network, fstab or sudoers files."""
    targets = []
    for i, a in enumerate(args):
        if any(c in ">" for c in a) and all(c in "<>&|0123456789" for c in a) and i + 1 < len(args):
            targets.append(args[i + 1])
    files = positional(args[1:])
    if cmd in ("cp", "install", "ln"):
        targets += files[-1:]  # only the destination is written
    elif cmd in ("tee", "mv", "truncate", "rm") or (cmd in ("sed", "perl") and ("i" in short or "--in-place" in long_)):
        targets += files
    hits = sorted({t for t in targets if is_access_file(t) and not re.search(r"\.bak-\d{8}$", t)})  # rule-1 backups are fine
    return [Finding(DENY, f"`{cmd}` writes {', '.join(hits)}", access=True)] if hits else []


# --- decision ------------------------------------------------------------------------------

def guarded_hosts(command, profiles):
    """Hosts this command reaches, and whether the checks are off for all of them."""
    hosts = set()
    for seg in segments(command):
        args = unwrap(seg)
        if not args:
            continue
        name = os.path.basename(args[0])
        if name == "ssh":
            host, _ = ssh_split(args)
            if host:
                hosts.add(host)
        elif name in ("scp", "rsync"):
            hosts.update(a.split(":")[0].split("@")[-1] for a in positional(args[1:]) if re.match(r"^[\w.@-]+:", a))
    off = {f.get("access", "").split()[-1] for f, _ in profiles
           if f.get("guard") == "off" and f.get("access", "").startswith("ssh ")}
    return hosts, bool(hosts) and hosts <= off


def deny_reason(findings, irreversible):
    whats = "; ".join(f.what for f in findings)
    lines = [f"hsops guard: {whats}. This is disruptive (fixed rule 2). Before you retry, state in your reply:",
             "1. what this command changes, stops or deletes",
             "2. a one-line rollback",
             "3. the user's go-ahead for this exact command, quoted word for word"]
    if any(f.access for f in findings):
        lines.append("4. that the current session stays open, and how you'll prove the new state over a second connection (fixed rule 3)")
    if irreversible:
        lines.append("This destroys data permanently. For a block device, also name it by model and size as the user confirmed it (fixed rule 5).")
    lines.append("If you don't have that go-ahead, ask the user instead of retrying. The identical command, retried within 10 minutes, then runs once.")
    return "\n".join(lines)


def main():
    payload = _hook.read_payload()
    command = (payload.get("tool_input") or {}).get("command")
    if payload.get("tool_name") not in ("Bash", None) or not isinstance(command, str):
        return
    profiles = _hook.profiles()
    local = [f for f, _ in profiles if f.get("access") == "local"]
    hosts, all_off = guarded_hosts(command, profiles)
    if all_off or (local and all(f.get("guard") == "off" for f in local) and not hosts):
        return
    # Anything in a command that also uses ssh may be fed to the server (heredocs, pipes).
    remote = bool(hosts) or bool(local)
    ctx = Context()
    findings = [f for seg in segments(command) for f in check(seg, remote, ctx)]
    if not findings:
        return
    irreversible = [f for f in findings if f.tier == ASK]
    if irreversible and not _hook.is_codex(payload):
        _hook.emit(ASK, f"hsops guard: {'; '.join(f.what for f in irreversible)}. This destroys data permanently. "
                        "Check the target before approving (fixed rules 2 and 5).")
    state = _hook.State("guard", payload)
    k = _hook.key(command)
    if state.retry_allowed(k):
        state.save()
        return
    state.record_denial(k)
    state.save()
    _hook.emit(DENY, deny_reason(findings, bool(irreversible)))


if __name__ == "__main__":
    main()
