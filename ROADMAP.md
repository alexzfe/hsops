# Roadmap

Ideas to explore later. Each one needs its own design pass before it gets built.

## Fixes in visible Herdr panes

`fix` runs fixes one at a time in the main session (see DESIGN.md). When Herdr is running (`HERDR_ENV=1`), fixes could instead run as agents in their own visible panes, which the user can watch and step into. That is the natural way back to fixes in parallel, for plans that touch nothing in common.

- **Open questions:**
  - How approvals and guard-hook prompts reach the user from a pane.
  - How the coordinating session learns that a pane's fix finished, and its result.
