# Roadmap

Ideas to explore later. Each one needs its own design pass before it gets built.

## A less strict evidence hook

The evidence hook (`hooks/evidence.py`) denies the first write to every data-folder file in a session, and every write with a hedge phrase. In practice that may cost more turns than it saves. The idea is to loosen it without letting guesses back into the data folder.

- **Open questions:**
  - Which denials have caught a real guess, and which only cost a retry? Count them from past sessions first.
  - Whether some writes need no first-write check, such as sighting tags (dates only) or a changelog line that repeats the command it records.

## Fixes in visible Herdr panes

`fix` runs fixes one at a time in the main session (see DESIGN.md). When Herdr is running (`HERDR_ENV=1`), fixes could instead run as agents in their own visible panes, which the user can watch and step into. That is the natural way back to fixes in parallel, for plans that touch nothing in common.

- **Open questions:**
  - How approvals and guard-hook prompts reach the user from a pane.
  - How the coordinating session learns that a pane's fix finished, and its result.
