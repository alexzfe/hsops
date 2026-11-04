---
name: learn
description: Use when the user runs /hsops:learn, asks to remember what a homeserver session taught, wants to record that a lesson came up again, or wants hsops itself improved from a session, or when a homeserver task ended on a surprise worth keeping, such as a cause that wasn't obvious, a step that failed, a fact the profile lacked or a preference the user stated.
---

# Learn

Turns a session's surprises into lasting knowledge, written where the next session will read it. Read `../../shared/conventions.md` and `../../shared/learning-formats.md` (relative to this skill's directory) first.

Learn captures what this one session taught. It never clusters lessons into patterns, moves lessons between files, writes new skills or prunes; those are `/hsops:evolve`'s.

## 1. Harvest

List the candidates from this session. A **lesson** is something that would have saved time if it had been known at the start:

- a root cause that wasn't obvious
- a step that failed, and what worked instead
- a fact the profile lacked
- a preference the user stated
- a fixed rule the user knowingly overrode.

Alongside new lessons, list:

- **Sightings:** a lesson already on file that this session hit again or relied on. Record the occurrence on that line, never a near-duplicate.
- **Skill-edit candidates:** a missing step or check, a request that should have loaded a skill and didn't, or a skill line proven wrong. Each names its event and its target file. Learn never edits a skill: these go to the ledger, and evolve proposes them once they have a history.
- **Skill candidates:** a job the user asked for, or a review item, that no skill owns.

Record cost and risk as the learning formats say: pattern, skill and skill-edit candidates record `Cost:`, measured in the session, never estimated; a safety edit records `Severe:`, set only when data or access was at risk, plus `Cost:` when time was measured. A severe candidate becomes a ledger safety edit, never a new-skill candidate.

Keep only what looking can't reveal: drop anything that one command shows, things done right by default, and one-off outages.

Then apply the evidence rule from the conventions to each candidate:

- **Has evidence** (command output or a file seen this session, or the user's words): keep it.
- **Can be checked with a read-only command:** check it now, then keep it or drop it.
- **Inferred from the user's behaviour:** turn it into a question for the user. It's written only if they say yes.
- **Still unconfirmed** ("not verified", "may", "I don't know"): drop it. If it's worth knowing, mention it to the user in one line as an open question; it is not written.

**Done when:** each remaining candidate is one short sentence with its evidence named.

## 2. Route each candidate

Follow `references/routing.md`: the content test, the destinations table and maintainer mode. A missing target file is treated as empty and created only on an approved write.

## 3. Refine the target file

Read each target file first. Then choose, in this order of preference:

1. Edit an existing line that the lesson corrects or sharpens.
2. Delete a line that the lesson proves wrong or stale.
3. Add one line, placed next to the step it changes.

How lessons are written:

- as one line of about 20 words or fewer: a positive instruction, with the reason in a clause
- with no account of the session and no hedging.

General lessons and suite files contain no hostnames, IPs, usernames or secrets.

Size limits: a SKILL.md stays under about 100 lines and a reference file under about 150. When an edit would push a file past its limit, propose splitting a branch into its own reference file.

## 4. Approve and write

Present the edits as a brief in the message itself (see "Asking for approval" in the conventions), grouped by destination:

- for each lesson: one line saying what it is and why it matters, its pick (general or server) so the user can flip it, then its diff
- each sighting, skill edit and ledger entry, with its event, `Cost:` and any `Severe:`
- then a short question asking which of the edits to write.

Write only what the user approves. If the data folder or the suite is a git repo, point the user to `git diff` to review the edits before committing.

## 5. Offer to share upstream

For each general lesson that would help every hsops user, offer to draft an issue or PR against the hsops repository (`repository` in `.claude-plugin/plugin.json`). The draft contains only the lesson and its reason. Create it with `gh` only after the user approves. Skill edits are never drafted here; evolve drafts them once they are ready.

## 6. Point to evolve

When the ledger has a ready entry (see `## Ready and declined` in the learning formats), a severe one included, or 3 or more lessons share a topic within one skill's job, or a `lessons.md` or `general/` file passes about 40 lines, end with one line naming each, with its counts and cost:

`Ready for /hsops:evolve: 'rotate a leaked secret' (3 occurrences, 1 session, 25 min); a safety edit for secrets in git; 4 monitoring lessons cluster on SMART.`

**Done when:** every harvested candidate has been written, logged, shared or declined by the user.
