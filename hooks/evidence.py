#!/usr/bin/env python3
"""hsops evidence check: a PreToolUse hook on writes to the data folder (~/.config/hsops/).

It backs up the evidence rule in the conventions, following ECC GateGuard's fact-forcing pattern:

- The first write to each file in a session is denied, with questions for that kind of file
  (evidence for each line, the user's words for each preference). The questions differ for
  lessons, patterns, the ledger, `user.md` and server files. The retry then runs.
- Any write with hedged lines ("not verified", "probably", "I think") is denied once. Claude
  verifies or drops them, or says why a match isn't a hedge and retries the identical write.

Handles Write, Edit and MultiEdit, Codex's apply_patch, and Bash writes (`>>`, `tee`, `sed -i`).
"""

import json
import os
import re

import _hook
import guard

HEDGES = re.compile(
    r"\b(not verified|unverified|i think|i believe|probably|presumably|should be|seems? to|appears to"
    r"|i don['’]t know|i do not know|not sure)\b", re.IGNORECASE)

QUESTIONS = {
    "user": "for each preference you add or change, quote the user's words that state or confirm it. "
            "Drop any preference the user hasn't stated or confirmed.",
    "general": "the session event that taught each lesson (a command and its output, or the user's words), "
               "and why it applies beyond this one server.",
    "pattern": "the session events behind each pitfall (a command and its output), the check you ran and its output, "
               "or the lesson lines on file it was built from, quoted; "
               "and confirm no line names this server's hosts, IPs, paths or hardware serials.",
    "ledger": "for each occurrence, the user's words or the review item, its date, and its cost as measured this session, "
              "or, for a decline or an entry that leaves the ledger, the user's words; "
              "for a Severe line, the event that put data or access at risk.",
    "server": "for each line you add or change, its evidence: the command and the output line that shows it, "
              "or the user's words. Drop any line you can't name evidence for.",
}


def in_data_dir(path, cwd):
    path = os.path.expanduser(re.sub(r"^\$\{?HOME\}?", "~", path))
    root = os.path.realpath(_hook.data_dir())
    full = os.path.realpath(os.path.join(cwd or os.getcwd(), path))
    return full.startswith(root + os.sep)


def file_class(path):
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(_hook.data_dir()))
    if rel == "user.md":
        return "user"
    if rel.startswith(os.path.join("general", "patterns") + os.sep):
        return "pattern"
    if rel == os.path.join("general", "candidates.md"):
        return "ledger"
    return "general" if rel.startswith("general" + os.sep) else "server"


def new_lines(new, old=""):
    seen = set(old.splitlines())
    return [l for l in new.splitlines() if l.strip() and l not in seen]


def writes(payload):
    """(file path, new lines) for each data-folder file this tool call writes."""
    tool, inp, cwd = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("cwd")
    found = []
    if tool in ("Write", "Edit", "MultiEdit") and isinstance(inp.get("file_path"), str):
        if tool == "Write":
            lines = new_lines(inp.get("content") or "")
        elif tool == "Edit":
            lines = new_lines(inp.get("new_string") or "", inp.get("old_string") or "")
        else:
            lines = [l for e in inp.get("edits") or [] for l in new_lines(e.get("new_string") or "", e.get("old_string") or "")]
        found.append((inp["file_path"], lines))
    elif tool == "apply_patch" and isinstance(inp.get("command"), str):
        current = None
        for line in inp["command"].splitlines():
            m = re.match(r"^\*\*\* (?:Add|Update) File: (.+)$", line)
            if m:
                current = (m.group(1).strip(), [])
                found.append(current)
            elif line.startswith("*** "):
                current = None
            elif current and line.startswith("+") and line[1:].strip():
                current[1].append(line[1:])
    elif tool == "Bash" and isinstance(inp.get("command"), str) and "hsops" in inp["command"]:
        for seg in guard.segments(inp["command"]):
            args = guard.unwrap(seg)
            if not args:
                continue
            cmd, short, _ = os.path.basename(args[0]), *guard.flags(args[1:])
            targets = [args[i + 1] for i, a in enumerate(args[:-1]) if ">" in a and all(c in ">&|0123456789" for c in a)]
            if cmd in ("tee", "cp", "mv", "install") or (cmd in ("sed", "perl") and "i" in short):
                targets += guard.positional(args[1:])
            found += [(t, new_lines(inp["command"])) for t in targets]
    return [(path, lines) for path, lines in found if in_data_dir(path, cwd)]


def main():
    payload = _hook.read_payload()
    targets = writes(payload)
    if not targets:
        return
    state = _hook.State("evidence", payload)
    k = _hook.key(payload.get("tool_name", ""), json.dumps(payload.get("tool_input"), sort_keys=True))
    if state.retry_allowed(k):
        state.save()
        return
    gated = state.data.setdefault("gated", [])
    cwd = payload.get("cwd") or os.getcwd()
    reasons = []
    for path, lines in targets:
        full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
        rel = os.path.relpath(full, os.path.realpath(_hook.data_dir()))
        if full not in gated:
            gated.append(full)
            reasons.append(f"First write to {rel} this session. Before you retry, present in your reply: "
                           + QUESTIONS[file_class(full)])
        hedged = [l.strip().lstrip("-*+ ") for l in lines if HEDGES.search(l)]
        if hedged:
            reasons.append(f"Hedged lines for {rel}:\n" + "\n".join(f"  - {l}" for l in hedged)
                           + "\nCheck each with a read-only command or ask the user, then write it plainly, or drop it. "
                             "If a match isn't a hedge (a quote from docs, say), state that in your reply.")
    if not reasons:
        state.save()
        return
    state.record_denial(k)
    state.save()
    _hook.emit("deny", "hsops evidence check (conventions: Evidence).\n" + "\n".join(reasons)
               + "\nThen retry the identical write; it runs once.")


if __name__ == "__main__":
    main()
