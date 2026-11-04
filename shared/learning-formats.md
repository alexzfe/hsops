# hsops learning formats

Shared reference for the `learn` and `evolve` skills. These are the shapes of what a session teaches and how it is counted.

## Sightings

A lesson stays one short line, with a sighting tag at the end:

```
- Scripts fed to `ssh <server> bash -s` lose lines to anything reading stdin; add `</dev/null`. (seen 2026-11-01, 2026-11-03 ×2)
```

- The first date is when the lesson was written. Each later date is a session that hit it again or relied on it.
- `×N` records N distinct occurrences in that session.
- The tag doesn't count toward the ~20-word limit.

## Occurrences

- **Each distinct occurrence counts**, several per session included. Three different leaked secrets in one review are 3 occurrences.
- **Repeat mentions don't count again.** N19 in the review, the fix plan and the summary is 1 occurrence.
- **Key.** An occurrence is keyed by its date and its event (the review item, or the command and its output). A key already recorded is not added again, so a second learn run in the same session adds nothing.
- **Show the spread.** Counts always come with their sessions: `5 occurrences, 3 sessions`, so a burst from one session reads as one.

## Cost and severe

Two facts replace any notion of importance. Each is taken from the session.

- **`Cost:`** the time an occurrence took, as measured in the session: `Cost: 9 min (plan agent rediscovered it)`, `Cost: 2 retries`. Pattern and skill candidates record Cost; a safety edit records Severe, plus Cost only when the occurrence took measurable time.
- **`Severe:`** set only when data or access was at risk, with its event: `Severe: a dying disk would have gone unnoticed`.

They do different jobs, because **skills streamline; checks make things safe.** A new skill doesn't make a risk smaller; it makes a bumpy process smooth. Safety lives in the fixed rules, the hooks, the review dimensions and `fix`'s verify step.

- **Patterns and new skills** are eligible on recurrence and cost alone: 2 or more occurrences, ordered by cost × occurrences. `Severe` never makes one eligible.
- **Safety edits** are eligible after one severe occurrence. `Severe` makes only a safety edit eligible. A safety edit is a skill edit that prevents the problem:
  - a check in a review dimension
  - a step in the skill that ran into it
  - a `tests/guard-cases.txt` line for a command that should have been stopped
  - rarely, a proposed fixed rule.
- Severe entries sort first among skill edits.
- Counts decide **eligibility** only. They never rank by themselves.

## Patterns

Multi-step recipes. In the suite: `skills/<skill>/references/patterns/<topic>.md`. In the data folder: `general/patterns/<skill>/<topic>.md`. 20–60 lines, at most ~150. The filename is the index.

```
# SMART self-tests on mixed disks
When: scheduling self-tests, or exporting their results, on SATA, USB-bridged or NVMe disks.
Steps: <numbered, with exact commands>
Pitfalls: <each with the condition it applies to>
Check: <command → expected result>
Seen: 2026-11-03
```

Patterns hold general knowledge only. Machine-specific facts stay in `lessons.md`, which links to the pattern in one line.

## Ledger

`general/candidates.md` holds what is waiting to become a pattern, a skill or a safety edit:

```
## Skill: rotate a leaked secret
Trigger: "my token leaked", "rotate the API keys"
Cost: 25 min across N19, N18, N12 (finding each use, rotating, re-checking)
Seen: 3 occurrences, 1 session. 2026-11-03 review N19, N18, N12

## Pattern: monitoring/textfile-metrics
Lessons: <server> "node-exporter merges a metric name across textfile files…"; <server> "a fake-alert test file must copy HELP and TYPE…"
Cost: 15 min (a fake-alert test silently dropped samples)
Seen: 2 occurrences, 2 sessions. 2026-11-01, 2026-11-03

## Safety edit: credentials committed to git
Severe: service API keys committed to tracked config files
Proposed: data-safety dimension check for secrets in tracked files
Seen: 1 occurrence. 2026-11-03 review N18
```

## Ready and declined

An entry is **ready** at 2 or more occurrences, or, for a safety edit, at one severe occurrence. It leaves the ledger when built (`built: <path>`) or covered by something else.

**Declines don't block for good.**

- A declined entry stays with `Declined YYYY-MM-DD: "<reason>"` and keeps counting. Occurrences before and since the decline are shown apart.
- It is proposed again once 2 or more new occurrences arrive after the decline (or, for a safety edit, one new severe occurrence). The earlier reason is shown next to the new evidence.
- Time alone never re-proposes it.
- The user can ask for any declined entry at any time.
