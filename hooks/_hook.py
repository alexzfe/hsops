"""Shared helpers for the hsops hooks: the payload, decisions, the data folder and per-session state."""

import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import time

RETRY_WINDOW = 600  # seconds an identical retry stays allowed after a denial


def read_payload():
    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def is_codex(payload):
    # Codex sends turn_id with every tool hook; Claude Code doesn't.
    return "turn_id" in payload


def emit(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def data_dir():
    return os.environ.get("HSOPS_DATA_DIR") or os.path.expanduser("~/.config/hsops")


def profiles():
    """Every server profile as (front matter dict, full text)."""
    found = []
    for path in sorted(glob.glob(os.path.join(data_dir(), "servers", "*", "profile.md"))):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        front = {}
        parts = text.split("---", 2)
        if text.startswith("---") and len(parts) == 3:
            for line in parts[1].splitlines():
                key, sep, value = line.partition(":")
                if sep:
                    front[key.strip()] = value.strip()
        found.append((front, text))
    return found


def key(*parts):
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()


class State:
    """Small JSON state file per hook and session, so denials can be retried."""

    def __init__(self, hook, payload):
        base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "hsops-hooks")
        session = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("session_id") or "none"))[:80]
        self.path = os.path.join(base, f"{hook}-{session}.json")
        try:
            with open(self.path, encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            self.data = {}
        now = time.time()
        denied = self.data.setdefault("denied", {})
        for k in [k for k, t in denied.items() if now - t > RETRY_WINDOW]:
            del denied[k]

    def retry_allowed(self, k):
        """True once for something denied within the retry window; the retry is then used up."""
        return self.data["denied"].pop(k, None) is not None

    def record_denial(self, k):
        self.data["denied"][k] = time.time()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            tmp = f"{self.path}.{os.getpid()}"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f)
            os.replace(tmp, self.path)
        except OSError:
            pass
