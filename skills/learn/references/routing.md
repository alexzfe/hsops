# Routing

Where each candidate from learn's harvest is written. Formats are in `../../../shared/learning-formats.md`.

## Content test

Decide each lesson by what it is about, not by how sure you feel:

- **How software behaves** (a tool, a daemon, a file format, a hardware class): general.
- **This machine's paths, hardware, layout or choices:** the server's `lessons.md`.
- **Mixed:** split it. The general part goes up with its condition attached, and the machine's part stays in `lessons.md`. For example, "some NVMe drives reject namespace 1 for self-tests; use the broadcast namespace (-d nvme,0xffffffff)" is general, while "this server's data disk is one of them" stays on the server.

Strip hostnames, IPs, serials, usernames and personal paths from anything general; write `<server>` where a name is needed.

The brief shows each lesson's pick, general or server, so the user can flip it.

## Destinations

| Candidate | Destination |
|---|---|
| A fact about the server | its `profile.md` |
| True only for this server, including rule overrides | its `lessons.md` |
| How this user likes things done, as stated or confirmed by them | `~/.config/hsops/user.md` |
| True for any homeserver | `~/.config/hsops/general/<skill>.md`, for the skill that was running when the lesson mattered |
| A sighting of a lesson already on file | that lesson's line: add the occurrence to its tag, never a near-duplicate line |
| A skill edit from one event | the skill's own files (see Maintainer mode), naming its event |
| A skill candidate, or a severe candidate as a safety edit (unless that edit is written this session as an approved skill edit) | `~/.config/hsops/general/candidates.md`, the ledger |

A ledger entry that already exists gets the new occurrence added to its `Seen:` line, keyed as in `## Occurrences`, rather than a second entry.

Skill edits that come from a cluster of lessons are evolve's, not learn's. So are patterns, moves between files, new skills and pruning.

## Maintainer mode

The user is a maintainer when this skill's directory is inside a git checkout of hsops and not in a plugin cache: `git -C <skill dir> rev-parse --show-toplevel` succeeds, and the path doesn't contain `/cache/`.

- **Maintainer:** general lessons and skill edits go straight into the suite file where they would have been read: any `SKILL.md` or reference (a setup phase, `add-service/references/apps/<app>.md`, a review dimension file, diagnose's common causes) or `shared/conventions.md`.
- **Plugin user:** general lessons go to `general/`. Skill edits become an upstream draft, an issue or PR against the hsops repository (`repository` in `.claude-plugin/plugin.json`), created with `gh` only after the user approves.
