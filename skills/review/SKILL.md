---
name: review
description: Use when the user wants their whole homeserver reviewed, audited, explored or optimized in depth, or asks about one area of it in depth (data safety, security, reliability, performance, efficiency, networking, maintainability or observability), such as "check my security" or "is it wasting power". Not when they ask for a quick check (quick-review) or about changes just made (review-changes).
---

# Review

A deep look at one whole server: a shared snapshot, one reviewer per dimension, then recommendations merged and ranked by the user's priorities. Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context, including the newest file in `servers/<server>/reviews/`.

## 1. Priorities

Confirm the profile's Priorities with the user, or settle them in a Discovery round (conventions):

- what matters most: data safety, security, reliability, performance, power and cost, low upkeep, noise
- constraints: budget, fixed hardware, times when downtime isn't acceptable.

Save the answers to the profile.

Then choose the dimensions:

- a review of the whole server runs all eight in `references/dimensions/`, unless the user narrows it
- a request about one area runs that dimension only.

**Done when:** the priorities are saved and the dimensions are listed.

## 2. Snapshot

Every dimension judges the same moment from this one snapshot, so no command runs once per agent. Collect `references/snapshot.md` in as few SSH calls as possible, and write the result to the scratchpad as `snapshot-<server>.md`. Mask every secret value (`.env` contents, passwords in compose `environment:` sections) before writing.

**Done when:** every section of snapshot.md is filled, or marked unavailable with the reason.

## 3. Dimension reviews

- **With subagents (Claude Code):** start one `hsops:reviewer` agent per chosen dimension, all in parallel, in a single message. Give each one the absolute paths of:
  - its `references/dimensions/<dim>.md`
  - the snapshot
  - `shared/conventions.md`
  - the profile
  - the last review
  - `../add-service/references/apps/<app>.md` for each installed app.
  
  Also give it the user's priorities and the server's `access:` value.
- **Without subagents (Codex):** go through the dimensions one at a time in this session, each following its own file.

**Done when:** every chosen dimension has returned its findings, or reported as failed with the reason.

## 4. Merge

- **No evidence, no finding:** a finding without an evidence line is dropped and listed under Not checked.
- **Duplicates:** a problem reported by several dimensions becomes one finding that lists them all.
- **Conflicts** (Security wants a port closed, Reliability needs it open; Efficiency wants disks spun down, Performance doesn't): present each one to the user as a choice, with a lean based on their priorities.
- **The last review:**
  - leave out items the user declined, unless the evidence has changed (and say what changed)
  - for items marked done, check that the fix is still in place
  - items marked failed carry over as open, with the failed check noted.
- **Ranking:** order findings by impact against the user's priorities.

## 5. Report and save

Present the report:

```
## Review: <server> (<date>)
Priorities: <...>   Dimensions: <...>
### Fix now     risk to data or access
### Recommended
### Optional
### Choices     conflicts between dimensions, each with a lean
### Not checked skipped checks, and findings based on a snapshot only
```

Write each finding as: **title**, the dimensions that raised it, evidence, the suggested change, which skill carries it out, and effort (S, M or L).

Save it to `servers/<server>/reviews/YYYY-MM-DD.md`, with every recommendation marked `open`. Later statuses are `done`, `declined: <reason>` and `failed: <check that failed>`. Point the review line in `backlog.md` at the new file (conventions).

**Done when:** the report has been presented and saved.

## Acting on it

When the user picks recommendations, hand them to the `fix` skill. Optimizations follow fixed rule 7. Mark items the user turns down `declined: <reason>`.
