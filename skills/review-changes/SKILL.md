---
name: review-changes
description: Use at the end of any task that changed a homeserver, or when the user asks to review the changes or check what was just done on it.
---

# Review changes

One reviewer looks only at what a task changed, from a clean context, so the session that made a change isn't the only one to judge it. Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context.

## 1. Gather

Collect the changes: this task's `changelog.md` lines, the plans or commands run, and the baseline file if there is one. Started on its own, use what the user names, or else the changelog lines since the date of the newest file in `reviews/`.

**Done when:** the list of changes is complete. With no changes to review, say so and stop.

## 2. Review

- **With subagents (Claude Code):** start one `hsops:reviewer` agent in **changes** mode. Give it the changes, the server's `access:` value, the baseline if there is one, and the absolute paths of `shared/conventions.md`, the profile and `../review/references/dimensions/`.
- **Without subagents (Codex):** follow the Changes mode in `../../agents/reviewer.md` in this session.

**Done when:** the review has returned, or reported as failed with the reason.

## 3. Report and save

Show the user the result. When there are no problems, say so in a line and write nothing.

Otherwise, add each problem to the newest file in `reviews/` under a dated `## Changes review` heading, continuing its numbering and marked `open`. With no review file yet, start `reviews/YYYY-MM-DD.md`.

**Done when:** the result has been shown and any problems saved.
