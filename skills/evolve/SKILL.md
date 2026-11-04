---
name: evolve
description: Use when the user runs /hsops:evolve, asks to turn lessons into patterns or new skills, or when learn reports entries ready for evolve.
---

# Evolve

Consolidates what learn has gathered into lasting changes: promotions to general, patterns, skill edits, safety edits, new skills and prunes. Read `../../shared/conventions.md`, `../../shared/learning-formats.md` and `../learn/references/routing.md` (relative to this skill's directory) first.

Each learning takes the lowest level that holds it: a lesson, a pattern inside an existing skill's job, a skill edit, or a new skill. The line between a pattern and a new skill is the trigger, not size or frequency. Skills streamline; checks make things safe.

## 1. Gather

Read the whole data folder: every `servers/*/lessons.md`, `general/*.md`, `general/patterns/` and `general/candidates.md`. A missing file or folder counts as empty. Also read each suite skill's `description` and list its `references/`. Build four lists:

- **Ready:** ledger entries that are ready (`## Ready and declined` in the formats), including declined ones with enough new occurrences since the decline.
- **Clusters:** 3 or more lessons on one topic within one skill's job.
- **Promotions:** lessons in `lessons.md` that pass the `## Content test` in learn's routing file, general or mixed. The first run works through the whole backlog this way.
- **Prunes:** duplicates, lessons the profile or the suite now covers, and lessons proven wrong.

**Done when:** every entry in the data folder is in a list or seen to need nothing.

## 2. Place

Put each entry on the ladder at the lowest level that holds it.

- **New skill:** only when it passes the **trigger test**, written out in the brief:
  1. 2–3 phrases a user would say to ask for this job.
  2. The closest existing skill descriptions, quoted.
  3. Why none of them claims those phrases.

  An entry that fails becomes a pattern for, or an edit to, the skill that owns the job.
- **Safety edit:** goes where it prevents the problem: a check in a review dimension, a step in the skill that ran into it, a `tests/guard-cases.txt` line, or rarely a proposed fixed rule. Never a new skill. `Severe` never makes a pattern or a skill eligible.
- **Pattern or skill:** eligible at 2 or more occurrences (formats); below that it stays in the ledger.

**Done when:** each entry has a level and a target file, and each new skill has its trigger test written.

## 3. Order

Safety edits first. Then everything else by cost × occurrences, each shown with its session spread: `3 occurrences, 1 session, 25 min`. Counts decide eligibility only; they never rank by themselves.

**Done when:** the list is in that order, with counts, sessions and cost or severe event on each entry.

## 4. Draft

Check Maintainer mode in learn's routing file first: it decides where every draft goes.

- **Promotions:** the general part goes to `general/<skill>.md` (or the suite file, for a maintainer), with its condition attached. Mixed lessons split as the content test says; the machine's part stays in `lessons.md`.
- **Patterns:** in the shape in the formats. Strip hostnames, IPs, serials, model names tied to one machine, usernames and personal paths; write `<server>` where a name is needed. A general lesson the pattern absorbs is removed only when the pattern holds its whole content and its condition; otherwise keep it. A server lesson keeps its machine fact and gets a one-line pointer to the pattern.
- **Skill edits and safety edits:** as diffs against the skill's own files.
- **New skills:** follow the suite's rules: a trigger-only `description` starting "Use when…", under ~100 lines, "read conventions, load context" first, a `**Done when:**` per stage, modelled on an existing skill of the same kind (a flow like `fix`, a one-pass check like `quick-review`).
- **Independent check:** with subagents (Claude Code), each new-skill draft gets one general-purpose subagent pass before the brief, given CLAUDE.md "Rules for Changes", the trigger-only description rule and the written trigger test. In Codex, run that check in this session. Patterns and edits get none, because the user reviews them in the diff.
- **Where drafts go:** a maintainer's drafts go into suite files on a branch. For a plugin user, patterns go to `general/patterns/<skill>/<topic>.md`, and skill edits and new skills become upstream drafts.

**Done when:** every placed entry has a diff, or a draft that has had its check.

## 5. Approve

Present a brief in the message (see "Asking for approval" in the conventions), grouped as **Promotions**, **Patterns**, **Skill edits** (safety edits first), **New skills** and **Prunes**. Each item gets one line on why, with its cost or severe event and its count and sessions, then its diff. A re-proposed declined entry shows its earlier reason next to the new evidence. End with a short question asking which to write.

**Done when:** the user has said which items to write.

## 6. Write and record

Write only what is approved. Then update the ledger:

- built: `built: <path>`, and the entry leaves the ledger
- declined: `Declined YYYY-MM-DD: "<reason>"`; the entry stays and keeps counting.

On a maintainer's clone, follow the repo's change rules: a branch, the `CLAUDE.md` architecture line for a new skill, the four version fields kept equal, and a PR. If the data folder is a git repo, point the user to `git diff`.

**Done when:** every gathered entry is written, declined, or left with its reason ("1 occurrence, cost 3 min: waiting").
