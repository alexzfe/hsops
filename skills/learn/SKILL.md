---
name: learn
description: Use when the user runs /hsops:learn, asks to remember what a homeserver session taught, or wants hsops itself improved from a session, or when a homeserver task ended on a surprise worth keeping, such as a cause that wasn't obvious, a step that failed, a fact the profile lacked or a preference the user stated.
---

# Learn

Turns a session's surprises into lasting knowledge, written where the next session will read it. Read `../../shared/conventions.md` (relative to this skill's directory) first.

## 1. Harvest

List the candidate **lessons** from this session. A lesson is something that would have saved time if it had been known at the start:

- a root cause that wasn't obvious
- a step that failed, and what worked instead
- a fact the profile lacked
- a preference the user stated
- a fixed rule the user knowingly overrode.

Keep only what looking can't reveal: drop anything that one command shows, things done right by default, and one-off outages.

Then apply the evidence rule from the conventions to each candidate:

- **Has evidence** (command output or a file seen this session, or the user's words): keep it.
- **Can be checked with a read-only command:** check it now, then keep it or drop it.
- **Inferred from the user's behaviour:** turn it into a question for the user. It's written only if they say yes.
- **Still unconfirmed** ("not verified", "may", "I don't know"): drop it. If it's worth knowing, mention it to the user in one line as an open question; it is not written.

**Done when:** each remaining candidate is one short sentence with its evidence named.

## 2. Route each lesson

| Lesson | Destination |
|---|---|
| A fact about the server | its `profile.md` |
| True only for this server, including rule overrides | its `lessons.md` |
| How this user likes things done, as stated or confirmed by them | `~/.config/hsops/user.md` |
| True for any homeserver | `~/.config/hsops/general/<skill>.md`, for the skill that was running when the lesson mattered |
| Unsure whether it's general | the server's `lessons.md`. Promote it once it recurs on a second server. |

**Maintainer mode:** if this skill's directory is inside a git checkout of hsops and not in a plugin cache (`git -C <skill dir> rev-parse --show-toplevel` succeeds, and the path doesn't contain `/cache/`), general lessons go straight into the suite file where they would have been read: the setup phase or reference, `add-service/references/apps/<app>.md`, a review dimension file, or diagnose's common causes. Otherwise they go to `general/`.

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

- for each lesson: one line saying what it is and why it matters, then its diff
- then a short question asking which of the edits to write.

Write only what the user approves. If the data folder or the suite is a git repo, point the user to `git diff` to review the edits before committing.

## 5. Offer to share upstream

For each general lesson that would help every hsops user, offer to draft an issue or PR against the hsops repository (`repository` in `.claude-plugin/plugin.json`). The draft contains only the lesson and its reason. Create it with `gh` only after the user approves.

## 6. Prune

When a `lessons.md` or `general/` file passes about 40 lines:

- promote lessons that also hold on another server
- merge duplicates
- delete lessons that the profile or the suite now covers.

**Done when:** every harvested lesson has been written, shared or declined by the user.
