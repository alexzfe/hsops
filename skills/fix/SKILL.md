---
name: fix
description: Use when the user picks recommendations from a saved hsops review to carry out on the homeserver, such as "fix #6 and #7", "fix the open items" or "do the fix-now ones".
---

# Fix

Turns chosen review items into changes on the server, one at a time, with a check after each. Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context, including the newest file in `servers/<server>/reviews/` (or the one the user names).

## 1. Pick

List the chosen items from the review file, with their status. Items marked `open` or `failed` can be picked; ask before redoing one marked `done` or `declined`. Confirm the list with the user.

Look up the change level (conventions). At **read-only**, do steps 1 and 2 only, then hand over the plans as commands for the user to run.

**Done when:** the user has confirmed the items.

## 2. Plans

Draft one plan per item in this session, without changing anything. A fix is **high-risk** when it touches storage, boot, the network or access, or needs a reboot. With subagents (Claude Code), start one `hsops:reviewer` agent in **plan** mode per high-risk item, in parallel, on the most capable model (`opus`). Only high-risk items get one, because a plan agent costs about as much as a whole review dimension. Each plan follows the skill named in its finding and has this shape:

```
#### Plan: <finding title>   (skill: <skill>)
Touches: <files, services, disks>
Steps:
1. <exact command>   disruptive: yes/no
Rollback: <exact commands>
Success check: <command → expected output>
Dimensions touched: <...>
Trade-offs: <expected costs, e.g. more power draw>
```

When two plans touch the same file, service or disk, order them and say so.

**Done when:** every item has a plan, or is reported as not fixable with the reason.

## 3. Approve

Present all plans as a brief in the message, then ask a short question: approve all, approve some, or change one. The approval covers each plan exactly as written. At **ask first**, also confirm before each step that changes something.

When the guard hook stops an approved disruptive step, quote the user's approval of that plan in your reply, then retry. The hook asks for facts, and the quote is the fact it needs.

**Done when:** the user has approved the plans to run.

## 4. Baseline

Record the state before anything changes, so that later checks can tell a regression from something that was already broken. It runs after approval, so no checks go to plans the user turns down. Save it to the scratchpad as `baseline-<server>.md`:

- **Health:** running containers and their status, `systemctl --failed`, the data mounts the profile lists, SSH reachable, and `tailscale status` when the profile uses Tailscale.
- **Dimensions:** start one `hsops:reviewer` agent in **verify** mode per dimension the approved plans touch, all in parallel, and save the checks that pass now.

**Done when:** the baseline file holds both.

## 5. Run and check, one fix at a time

Carry out each approved plan yourself, in this session and in order, following its skill and the fixed rules (backups of config files, a changelog line, profile updates). Never hand a fix to a subagent: only you can stop and ask the user when a step surprises you, and the guard hook's prompts stay in the conversation.

- **Where you are:** the review file's statuses are the record of the batch. After the conversation is compacted, or whenever you're unsure, re-read them and the baseline file instead of trusting memory.
- **Deviations:** read-only or easily reversed adjustments (a missing `mkdir`, a different package name) are fine; note them for the result. A new disruptive step, or any change to the rollback, stops the run: report it and re-plan that item.

After each fix, check it:

1. the plan's success check passes
2. the finding's evidence command no longer shows the problem
3. the health check matches the baseline
4. high-risk fixes only: one `hsops:reviewer` agent in **verify** mode, given the baseline and the file of every dimension the fix touched, finds no check that passed in the baseline failing now. One agent per fix, not one per dimension, because these checks repeat for every high-risk fix in the batch. In Codex, run these checks in this session.

The fix **failed** if any check fails, or a step errored or needed a disruptive deviation. New findings unrelated to the fix, and the costs listed under Trade-offs, are not failures: note them for the closing review.

- **Passed:** mark the item `done` in the review file and go on to the next one.
- **Failed:** stop the whole batch. Show the user the failed check with its evidence, and the plan's rollback. Don't roll back without their go-ahead. Mark the item `failed: <check that failed>`. The remaining items stay `open`, and their plans are re-checked against the changed server before they run.

**Done when:** every approved item is `done`, or the batch stopped at a failure the user has seen.

## 6. Close

Run the `review-changes` skill, giving it the approved plans and the baseline file; after a failed batch, wait until the user has decided on the rollback. When a problem traces to a fix, use each plan's Touches to name it, and mark that item `failed: <check that failed>`.

Don't run the `review` skill unless the user asks for it: it would repeat the same day's open items, and it can't confirm scheduled jobs that haven't run yet.

Summarise what changed, any deviations, what the review found, and what's left. List anything that can't be confirmed yet, such as a scheduled job that hasn't run, with the command that confirms it and when it can run.

**Done when:** `review-changes` has finished and the summary is given.
