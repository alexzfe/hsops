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

**Decision:** carrying out review recommendations is its own skill, `fix`. The fixes run one at a time in the main session. Subagents only draft high-risk plans and verify (the `reviewer` agent's plan and verify modes), in parallel.

**Why a separate skill:** by the rule above, it's triggered differently ("fix #6 and #7", "fix the open items") and knows different things: the plan → approval → run → check loop, the baseline and the review statuses. Review knows dimensions and merging.

**Why no fixer agent:**

- Homeserver fixes are usually small and overlap: the same compose file, firewall or Docker daemon. Running them in parallel saves little time and adds risk.
- Permission prompts and guard-hook prompts from several agents at once, each labelled with a different agent, are hard to follow. Run in sequence, they read as one conversation.
- The main session can stop and ask when reality differs from the plan; a subagent can only report back.
- Parallel planning and parallel verifying already give most of the speed.

**When to revisit:** a visible, separate pane per fixer (see the Herdr entry in ROADMAP.md) would answer the "hard to follow" problem, once the in-session version has proven itself.

## Three review skills, and agents only where the risk is

**Decision:**
- `review` looks at the whole server with eight agents. `quick-review` takes one pass with no agents. `review-changes` starts one agent on what a task just changed.
- A quick review appends to the newest review file instead of starting its own.
- `fix` drafts plans in the main session, and uses plan agents and per-fix verify agents only for high-risk fixes. After a high-risk fix, one verify agent covers every dimension it touched.
- The baseline runs after approval.
- Every task that changes the server, in any skill, closes with `review-changes`. `review` never starts by itself.

**Why separate skills:** by the rule above, each is triggered differently and knows different things: the dimensions and merging, a fixed checklist, and a look at one task's changes. The price is two more descriptions loaded in every session.

**Why:** one tested fix batch of eight items spawned 30 agents and used more tokens than the full review that produced it (1.57M against 1.18M fresh input). Each plan agent cost about as much as a whole review dimension, and four of the eight plans were never carried out. A closing `review` on top would have repeated the same day's open items, and it couldn't confirm the scheduled jobs that hadn't run yet.

**Why one verify agent per high-risk fix:** one per touched dimension multiplied with the number of high-risk fixes; three such fixes touching three dimensions each started nine. A single agent reruns only the baseline's passing checks for those dimensions, which is a short list. The baseline keeps one agent per dimension, because it runs once and has to cover each dimension's full checks.

**Why still review every change:** the session that made a change shouldn't be the only one to judge it. One agent starts from a clean context, so it reads the changes without the session's assumptions, and it replaces an end-of-batch verify agent per dimension.

**Why append:** `fix` and the next review read only the newest file. A separate quick report would hide older open and declined items, and copying them forward costs more than the quick review saves.

**The cost:** a regression from a low-risk fix may only show in the closing review, where it's harder to trace to one fix. The plans' Touches lists narrow it down. `quick-review` also skips tuning, power and long-term upkeep, which is why it names the dimensions it didn't cover. A plain "review my server" now starts the eight agents, so it stays the expensive path.

## The evidence hook forces facts instead of only matching hedge words

**Decision:** the evidence hook (`hooks/evidence.py`) denies the first write to each data-folder file in a session, with questions for that kind of file: the evidence for each line, the user's words for each preference in `user.md`, and the event behind each general lesson. The retry runs. Separately, any write with hedge phrases ("not verified", "probably", "I think") is denied once.

**Why:** a model's guesses rarely announce themselves, so matching hedge words alone misses most of them. GateGuard's finding is that demanding specific facts changes what the model writes, where "are you sure?" doesn't. The hedge check stays as a cheap second net, because the first test failed with exactly those phrases. Both allow an identical retry, so a false alarm costs one turn.

**What a hook can't check:** whether the user really said something. "Stated or confirmed by the user" stays an instruction.

## Skill descriptions say when, not what

**Decision:** every skill's `description` starts with "Use when…" and lists triggers, symptoms and app names. It never summarizes the skill's steps.

**Why:** superpowers measured that an agent given a description that summarizes the workflow follows the summary and skips the body. In their test, a skill that required two reviews ran one. Our `fix` description summarized its steps without the baseline or the closing `review-changes`, the two steps most likely to be skipped. The three review skills are told apart by their triggers ("a quick check", "in depth", "changes just made") instead of by how they work.

## Reviewer agents run on Sonnet; high-risk plans on Opus

**Decision:** `agents/reviewer.md` sets `model: sonnet`. The `fix` skill starts plan-mode agents for high-risk items on `opus`.

**Why:** with no `model:`, every reviewer inherited the session's model, and a whole review starts eight of them. Review, verify and changes modes read a snapshot and run read-only checks against a written dimension file, which doesn't need the most capable model. A high-risk plan touches storage, boot, the network or access, where a wrong step can lock the user out, so it gets the strongest one.

## Discovery in rounds, with a recommended answer to each question

**Decision:** the conventions' Discovery section asks in rounds. Each round holds every question that doesn't depend on another open one, each with a recommended answer and its reason. Facts come from the profile and read-only commands, never from the user. Question lists in skills are ground to cover, not a script.

**Why:** the skills used to list five or more things to "ask about" with no pacing, which tends to become one long questionnaire, including questions a command answers (`storage.md` asked about RAM after phase 1 had recorded it). The rounds come from the grilling skill. The recommendations come from superpowers' brainstorming: a default the user never heard is one they couldn't reject.

**The alternative:** brainstorming asks one question per message. That's slower when several questions are independent, which is common in setup.
