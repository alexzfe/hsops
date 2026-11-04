# Learn and evolve: lessons that grow into patterns and skills

**Date:** 2026-11-03 | **Status:** design approved in chat, spec awaiting review | **Target version:** 0.6.0

## Goal

What hsops learns in sessions should build up into knowledge that later sessions start from, as ECC's continuous learning does, while every line still rests on evidence. Repeated lessons grow into multi-step **patterns**, into **edits** to existing skills, and, when a job has no skill, into **new skills** for people building and operating homeservers.

It serves both the user's own sessions (data folder) and every hsops user (the suite). General knowledge moves from the first to the second.

### The problem today

- `learn` routes "unsure whether it's general" lessons to the server's `lessons.md` and promotes them only when they recur on a second server. With one server, nothing is ever promoted. On the maintainer's own data: 16 lessons in `lessons.md`, at least 5 of them general, and `general/` empty.
- Lessons are capped at one line. A multi-step recipe (SMART self-tests on USB-bridged and NVMe disks, which took a 9-minute plan agent to rediscover) gets split into one-liners that lose their connection to each other.
- Learn's maintainer mode writes only to some suite files (setup, app references, review dimensions, diagnose). It can't change other skills' steps, monitoring, backups or `conventions.md`.
- Nothing proposes a new skill when users keep asking for a job no skill owns.

### Non-goals

- **No passive observer.** Unlike ECC, no hook logs every tool call and no background agent infers patterns from it. Inferred patterns are the guesses the evidence rule keeps out (DESIGN.md), and homeserver sessions are full of secrets that such a log would capture.
- **No time decay.** A lesson isn't less true for going unseen. Pruning stays evidence-based.
- **No injecting lessons at session start.** Skills already load `lessons.md` and now patterns when they run.
- Loosening the evidence hook is a separate idea (ROADMAP.md).

## The ladder

Each learning takes the lowest level that holds it:

| Level | Changes | Lives in | Example |
|---|---|---|---|
| Lesson | Knowledge, one line | `lessons.md` or `general/<skill>.md` | `ssh host bash -s` loses lines to stdin; add `</dev/null` |
| Pattern | A multi-step recipe inside an existing skill's job | `references/patterns/` | SMART self-tests on mixed disks, under `monitoring` |
| Skill edit | A skill's steps, checks, triggers or wrong lines | the skill's own files | a `docker compose up -d --dry-run` step before applying an `.env` change |
| New skill | A job a user asks for that no skill's trigger claims | `skills/<name>/` | rotating a leaked secret |

The line between a pattern and a new skill is the **trigger**, not size or frequency: a recipe that a user would only ask for while doing an existing skill's job stays a pattern, however long it gets.

## Data shapes

### Lessons

Unchanged one-line shape, with a sighting tag at the end:

```
- Scripts fed to `ssh host bash -s` lose lines to anything reading stdin; add `</dev/null`. (seen 2026-11-01, 2026-11-03 ×2)
```

- The first date is when the lesson was written; each later date is a session that hit it again or relied on it. `×N` records N distinct occurrences in that session.
- The tag doesn't count toward the ~20-word limit.

### Occurrences

- Each **distinct** occurrence counts, several per session included. Three different leaked secrets in one review are 3 occurrences.
- Repeat mentions of the same occurrence don't count again: N19 in the review, the fix plan and the summary is 1 occurrence.
- Counts are always shown with their session spread: `5 occurrences, 3 sessions`, so a burst from one session reads as one.

### Impact

Every lesson, pattern and ledger entry candidate records its impact as a fact, with the event behind it:

- `data`: data loss or a near miss
- `access`: a lockout, or exposed credentials
- `outage`: a service down, or a failure that would have gone unnoticed
- `time`: rework or rediscovery

Counts decide **eligibility** only. Impact decides **order**. A `data` or `access` entry is eligible after one occurrence.

### Patterns

`skills/<skill>/references/patterns/<topic>.md` in the suite; `general/patterns/<skill>/<topic>.md` in the data folder. 20–60 lines, at most ~150. The filename is the index.

```
# SMART self-tests on mixed disks
When: scheduling self-tests, or exporting their results, on SATA, USB-bridged or NVMe disks.
Steps: <numbered, with exact commands>
Pitfalls: <each with the condition it applies to>
Check: <command → expected result>
Seen: 2026-11-03
```

Patterns hold general knowledge only. Machine-specific facts stay in `lessons.md`, which links to the pattern in one line.

### Ledger

`general/candidates.md` holds what is waiting to become a pattern or a skill:

```
## Skill: rotate a leaked secret
Trigger: "my token leaked", "rotate the API keys"
Impact: access (three service credentials exposed in a transcript and in git)
Seen: 3 occurrences, 1 session. 2026-11-03 review N19, N18, N12

## Pattern: monitoring/textfile-metrics
Lessons: <server> "node-exporter merges a metric name across textfile files…"; <server> "a fake-alert test file must copy HELP and TYPE…"
Impact: time
Seen: 2 occurrences, 2 sessions. 2026-11-01, 2026-11-03
```

An entry is **ready** at 2 or more occurrences, or at one `data` or `access` occurrence. It leaves the ledger when built (`built: <path>`) or covered by something else.

**Declines don't block for good.** A declined entry stays with `Declined YYYY-MM-DD: "<reason>"` and keeps counting, with occurrences before and since the decline shown apart. It is proposed again once 2 or more new occurrences, or one new `data` or `access` occurrence, arrive after the decline, with the earlier reason shown next to the new evidence. Time alone never re-proposes it. The user can ask for any declined entry at any time.

## `learn` changes

Learn keeps one job: capture what this session taught.

1. **Harvest** adds three candidate kinds to new lessons:
   - **Sightings:** a lesson on file this session hit again or relied on. Add the occurrence to its tag instead of a near-duplicate line.
   - **Skill-edit candidates:** a missing step or check, a request that should have loaded a skill and didn't, or a skill line proven wrong. Each names its event.
   - **Skill candidates:** a job the user asked for, or a review item, that no skill owns. These go to the ledger.

   Each candidate records its impact. The evidence rule is unchanged.
2. **Route.** The content test replaces "unsure → `lessons.md`": a lesson about how software behaves is general; one about this machine's paths, hardware or choices stays in `lessons.md`. A mixed lesson is split, the general part going up with its condition attached (for example, "some NVMe drives reject namespace 1 …"). Skill edits: on a maintainer's clone, edit the suite file directly (any `SKILL.md`, reference or `conventions.md`); for plugin users, draft an upstream issue or PR. Skill candidates go to the ledger.
3. **Refine** and 4. **Approve** as today. The brief adds sightings, skill edits and ledger entries, and shows each lesson's general-or-server pick so the user can flip it.
5. **Upstream** unchanged.
6. **Prune** moves to `evolve`.

**New closing line:** when an entry is ready, or 3 or more lessons share a topic within one skill's job, learn says so in one line: *"Ready for /hsops:evolve: 'rotate a leaked secret' (access, 3 occurrences); 4 monitoring lessons cluster on SMART."*

Small skill edits from a single event stay in learn, because they are clearest right after the session. Edits that come from a cluster of lessons belong to evolve.

**Size:** learn is 81 lines. The routing table and the maintainer and plugin-user rules move to `skills/learn/references/routing.md`, keeping `SKILL.md` under 100.

## The `evolve` skill

**Description:** "Use when the user runs /hsops:evolve, asks to turn lessons into patterns or new skills, or when learn reports entries ready for evolve."

1. **Gather.** Read `conventions.md` and the whole data folder (every `lessons.md`, `general/*.md`, `general/patterns/`, `general/candidates.md`), plus each suite skill's description and `references/` listing. Build four lists:
   - ready ledger entries, including declined ones with enough new occurrences
   - clusters: 3 or more lessons on one topic within one skill's job
   - promotions: lessons in `lessons.md` that pass the content test (the first run works through the existing backlog this way, with no migration script)
   - prunes: duplicates, lessons the profile or suite now covers, lessons proven wrong
2. **Place** each entry on the ladder. A new skill passes the **trigger test** in writing: 2–3 phrases a user would say, the closest existing skill descriptions quoted, and why none of them claims those phrases. An entry that fails becomes a pattern for, or an edit to, the skill that owns the job.
3. **Order** by impact, then occurrences, showing the session spread.
4. **Draft.**
   - Patterns in the shape above. General lessons they absorb are removed from their files, not copied. Server lessons get a one-line pointer.
   - Skill edits as diffs.
   - New skills follow the suite's rules: a trigger-only description, under ~100 lines, "read conventions, load context" first, a "Done when" per stage, modelled on an existing skill of the same kind.
   - With subagents, each new-skill draft gets one independent `hsops:reviewer` pass before the brief. Patterns and edits don't, because the user reviews them in the diff.
   - On a maintainer's clone, drafts go into suite files on a branch. For plugin users, patterns go to `general/patterns/`, and skill edits and new skills become upstream drafts.
5. **Approve.** A brief grouped as Promotions, Patterns, Skill edits, New skills and Prunes. Each item gets one line on why, with impact and count, then its diff. Then a short question.
6. **Write and record.** Write only what is approved. Update the ledger with `built: <path>` or `Declined YYYY-MM-DD: "<reason>"`. On a clone, follow the repo's change rules: the `CLAUDE.md` architecture line for a new skill, the four version fields, a branch and a PR.

**Done when:** every gathered entry is written, declined, or left with its reason ("1 occurrence, `time` impact: waiting").

## Other changes

- **`hooks/evidence.py`:** `general/patterns/**` and `general/candidates.md` already fall under the `general` class. Give each its own first-write question:
  - patterns: the session events behind each pitfall, and the check that was run
  - ledger: each occurrence (the user's words or the review item) and the event behind its impact

  The hedge check is unchanged.
- **`tests/run.py`:** cases for the first write to a pattern file, the first write to `candidates.md`, and a hedged line in a pattern.
- **`shared/conventions.md`:**
  - In Load context first, one new line: list this skill's `references/patterns/` and `general/patterns/<skill>/`, and read any whose name matches the task.
  - In Data folder, the layout of `general/patterns/` and `candidates.md`.
- **`DESIGN.md`:** a decision entry for the ladder, counts as eligibility and impact as order, no time decay, declines that reopen on new evidence, and no passive observer (the evidence rule, and secrets in logs).
- **`CLAUDE.md`:** architecture and key-file lines for `evolve/` and `learn/references/`.
- **`README.md`:** `/hsops:evolve` in the skills table; the developing note mentions patterns.
- **Version:** 0.6.0 in all four manifests and `CLAUDE.md`.

## Testing

- `python3 -B tests/run.py` passes, with the new evidence cases.
- Line limits: `learn/SKILL.md` and `evolve/SKILL.md` under ~100 lines; references under ~150.
- Both skills' descriptions start with "Use when…" and list triggers only.
- A read-through of learn then evolve, end to end.
- **Real-data run:** the first `/hsops:evolve` on the maintainer's data folder should, at minimum:
  - promote the software-behavior lessons to general: `docker inspect` health templates, `ssh bash -s` and stdin, node-exporter textfile HELP/TYPE merging, AppArmor blocking D-Bus
  - keep the machine-specific ones in `lessons.md`: a directory that looks like a mount, the deployment type of one app, the LAN fallback for SSH
  - split the NVMe namespace lesson into a general rule with its condition, and the drive model
  - propose a SMART pattern under `monitoring` (not a skill)
  - propose a secret-rotation skill (or log it as ready)

## Rollout

One PR on branch `learn-evolve`. After merge, the first `/hsops:evolve` run is the acceptance test on real data.
