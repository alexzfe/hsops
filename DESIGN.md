# Design decisions

Why hsops is built the way it is. Read this before restructuring.

## One `review` skill with dimension files, not one skill or agent per dimension

**Decision:**
- `review` is a single skill.
- Each of its eight dimensions is a reference file under `skills/review/references/dimensions/`.
- One generic `reviewer` agent is started once per chosen dimension, in parallel, from a shared snapshot.
- A merge step combines the results.
- A single dimension can still be run on its own, e.g. `/hsops:review security` or "check my security".

**Why:** the dimensions work as a set, not as independent specialists.

- **Same target, same moment.** Every dimension judges the same server, so they share one snapshot instead of each running the same commands again.
- **They conflict.** Security against Reliability, Efficiency against Performance. One coordinator has to set the findings side by side and present each conflict as a choice for the user. Separate agents never compare notes.
- **They usually run together.** "Review my server" means most of them, so independent triggering is worth little.
- **Context cost.** One skill description is loaded in every session, instead of eight.

**The alternative and when it's right:** ECC gives each specialist its own agent (`python-reviewer`, `go-reviewer`, …). That fits when each piece:
- is **triggered by something different**, such as a different file type, and rarely runs alongside the others
- **knows different things**, with little in common to share.

ECC still coordinates its reviewers for multi-angle reviews (`orch-review`). Its real cost is scale: dozens of always-loaded descriptions, pushy wording that starts agents too often, and boilerplate repeated in every file.

**The rule for hsops:**
- **Split** into a separate skill or agent when a piece is triggered differently *and* knows different things.
- **Keep one skill with reference files** when the pieces run together and have to be reconciled.
- App-specific checks stay as `## Review checks` sections in `add-service/references/apps/<app>.md` while they're small, so each app keeps a single file.

## A hybrid guard hook: `ask` for data loss, deny-once for the rest

**Decision:** the guard hook (`hooks/guard.py`) sorts disruptive commands into two tiers.

- **Permanent data loss** (formatting, wiping, `dd` to a device, destroying pools, datasets or volumes, `rm -r` on data paths) returns `ask`. The user sees the exact command and decides.
- **Everything else disruptive** is denied once, with a reason that makes Claude state what the command changes, the rollback and the user's go-ahead quoted word for word. The identical command, retried within 10 minutes, runs once. This is ECC GateGuard's pattern: demanding concrete facts works where asking the model "are you sure?" doesn't.

**Why:**

- Fixed rule 2 is an instruction, so a model that drifts can skip it. The hook catches the drift.
- Deny-once can't stop a model that wrongly believes it has approval; only a human can. That matters only where the damage is permanent, so `ask` is kept to that tier.
- False alarms cost differently. In the deny tier, one costs an extra turn, so that tier is broad. In the `ask` tier, a dialog for harmless commands teaches the user to click yes without reading, so that tier is narrow.
- GateGuard itself can't be reused: it doesn't look inside `ssh`, and it matches custom patterns only after removing quoted strings, where remote commands live. The guard uses `shlex` to read the remote command.

**Scope:** commands are checked inside `ssh`, `sh -c`, `docker exec` and heredocs fed to the server. On the workstation, only writes to block devices are checked (fixed rule 5), so cleaning up a local build folder never triggers it. A profile with `access: local` gets the full checks locally.

**Codex** can't return `ask` yet, so every match there is deny-once. Switch the data-loss tier to `ask` when Codex supports it.

## A separate `fix` skill, and no fixer agent

**Decision:** carrying out review recommendations is its own skill, `fix`. The fixes run one at a time in the main session. Subagents only draft plans and verify (the `reviewer` agent's plan and verify modes), in parallel.

**Why a separate skill:** by the rule above, it's triggered differently ("fix #6 and #7", "fix the open items") and knows different things: the plan → approval → run → check loop, the baseline and the review statuses. Review knows dimensions and merging.

**Why no fixer agent:**

- Homeserver fixes are usually small and overlap: the same compose file, firewall or Docker daemon. Running them in parallel saves little time and adds risk.
- Permission prompts and guard-hook prompts from several agents at once, each labelled with a different agent, are hard to follow. Run in sequence, they read as one conversation.
- The main session can stop and ask when reality differs from the plan; a subagent can only report back.
- Parallel planning and parallel verifying already give most of the speed.

**When to revisit:** a visible, separate pane per fixer (see the Herdr entry in ROADMAP.md) would answer the "hard to follow" problem, once the in-session version has proven itself.

## The evidence hook forces facts instead of only matching hedge words

**Decision:** the evidence hook (`hooks/evidence.py`) denies the first write to each data-folder file in a session, with questions for that kind of file: the evidence for each line, the user's words for each preference in `user.md`, and the event behind each general lesson. The retry runs. Separately, any write with hedge phrases ("not verified", "probably", "I think") is denied once.

**Why:** a model's guesses rarely announce themselves, so matching hedge words alone misses most of them. GateGuard's finding is that demanding specific facts changes what the model writes, where "are you sure?" doesn't. The hedge check stays as a cheap second net, because the first test failed with exactly those phrases. Both allow an identical retry, so a false alarm costs one turn.

**What a hook can't check:** whether the user really said something. "Stated or confirmed by the user" stays an instruction.
