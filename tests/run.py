#!/usr/bin/env python3
"""Run the hook tests: python3 tests/run.py. Run before every release."""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")

PROFILES = {
    "myserver": "---\nserver: myserver\naccess: ssh myserver\n---\n\n## Hardware\n- Disks: sdb 8 TB HDD, /tank, data\n\n## Layout\n- Stacks: /opt/stacks\n- Media / bulk storage: /tank/media\n",
    "pi": "---\nserver: pi\naccess: ssh pi\nguard: off\n---\n",
}

failures = 0
sessions = 0


def env(tmp):
    return dict(os.environ, HSOPS_DATA_DIR=os.path.join(tmp, "hsops"), CLAUDE_PLUGIN_DATA=os.path.join(tmp, "state"))


def run(tmp, hook, tool, tool_input, session=None, codex=False):
    """The hook's decision: ask, deny or allow."""
    global sessions
    if session is None:
        sessions += 1
        session = f"s{sessions}"
    payload = {"session_id": session, "tool_name": tool, "tool_input": tool_input}
    if codex:
        payload["turn_id"] = "t1"
    out = subprocess.run([sys.executable, "-B", os.path.join(HOOKS, hook)], input=json.dumps(payload),
                         capture_output=True, text=True, env=env(tmp), check=False)
    if out.returncode != 0:
        return f"error {out.returncode}: {out.stderr.strip()}"
    if not out.stdout.strip():
        return "allow"
    return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"]


def expect(name, got, want):
    global failures
    if got != want:
        failures += 1
        print(f"FAIL {name}\n     expected {want}, got {got}")


def guard_cases():
    cases, path = [], os.path.join(ROOT, "tests", "guard-cases.txt")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            if line[0].isspace():
                cases[-1][1] += "\n" + line.strip()
            else:
                want, command = line.split(None, 1)
                cases.append([want, command])
    return cases


def test_guard(tmp):
    for want, command in guard_cases():
        expect(command, run(tmp, "guard.py", "Bash", {"command": command}), want)
        codex_want = "deny" if want == "ask" else want
        expect(f"[codex] {command}", run(tmp, "guard.py", "Bash", {"command": command}, codex=True), codex_want)

    cmd = {"command": "ssh myserver 'sudo systemctl restart docker'"}
    expect("retry: first attempt", run(tmp, "guard.py", "Bash", cmd, "retry"), "deny")
    expect("retry: identical retry runs", run(tmp, "guard.py", "Bash", cmd, "retry"), "allow")
    expect("retry: used up after one run", run(tmp, "guard.py", "Bash", cmd, "retry"), "deny")
    other = {"command": "ssh myserver 'sudo systemctl restart docker containerd'"}
    expect("retry: an edited command is checked again", run(tmp, "guard.py", "Bash", other, "retry"), "deny")


def test_guard_local():
    """With `access: local`, Claude runs on the server, so local commands get the full checks."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "hsops", "servers", "box"))
        with open(os.path.join(tmp, "hsops", "servers", "box", "profile.md"), "w", encoding="utf-8") as f:
            f.write("---\nserver: box\naccess: local\n---\n")
        expect("[local] docker compose down", run(tmp, "guard.py", "Bash", {"command": "docker compose down"}), "deny")
        expect("[local] rm -rf /srv/media", run(tmp, "guard.py", "Bash", {"command": "sudo rm -rf /srv/media"}), "ask")
        expect("[local] docker ps", run(tmp, "guard.py", "Bash", {"command": "docker ps"}), "allow")


def test_evidence(tmp):
    data = os.path.join(tmp, "hsops")
    lessons = os.path.join(data, "servers", "myserver", "lessons.md")
    user = os.path.join(data, "user.md")
    plain = {"file_path": lessons, "content": "- The Immich ML container needs 4 GB of RAM.\n"}
    hedged = {"file_path": lessons, "old_string": "", "new_string": "- Backups probably run nightly.\n"}

    expect("evidence: outside the data folder", run(tmp, "evidence.py", "Write", {"file_path": "/tmp/x.md", "content": "probably"}), "allow")
    expect("evidence: first write to a file", run(tmp, "evidence.py", "Write", plain, "ev"), "deny")
    expect("evidence: its identical retry runs", run(tmp, "evidence.py", "Write", plain, "ev"), "allow")
    expect("evidence: later plain writes run", run(tmp, "evidence.py", "Edit", {"file_path": lessons, "old_string": "a", "new_string": "- Plex uses /dev/dri.\n"}, "ev"), "allow")
    expect("evidence: a hedged line", run(tmp, "evidence.py", "Edit", hedged, "ev"), "deny")
    expect("evidence: the hedged line's identical retry runs", run(tmp, "evidence.py", "Edit", hedged, "ev"), "allow")
    expect("evidence: a hedge already in the file isn't flagged",
           run(tmp, "evidence.py", "Edit", {"file_path": lessons, "old_string": "x probably y", "new_string": "x probably y\n- Disk sdb is 8 TB."}, "ev"), "allow")
    expect("evidence: first write to user.md", run(tmp, "evidence.py", "Write", {"file_path": user, "content": "- Experience: brief"}, "ev"), "deny")
    expect("evidence: Bash append to the changelog",
           run(tmp, "evidence.py", "Bash", {"command": f"echo '2026-10-30 restarted docker (it should be fine)' >> {data}/servers/myserver/changelog.md"}), "deny")
    expect("evidence: Bash read of the data folder", run(tmp, "evidence.py", "Bash", {"command": f"cat {data}/user.md"}), "allow")
    patch = f"*** Begin Patch\n*** Update File: {lessons}\n@@\n+- I think the UPS is a CyberPower.\n*** End Patch\n"
    expect("evidence: Codex apply_patch", run(tmp, "evidence.py", "apply_patch", {"command": patch}, codex=True), "deny")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in PROFILES.items():
            os.makedirs(os.path.join(tmp, "hsops", "servers", name))
            with open(os.path.join(tmp, "hsops", "servers", name, "profile.md"), "w", encoding="utf-8") as f:
                f.write(text)
        test_guard(tmp)
        test_evidence(tmp)
    test_guard_local()
    print("all hook tests passed" if not failures else f"{failures} failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
