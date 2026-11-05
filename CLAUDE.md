# hsops

**Version:** 0.6.2 | **Port:** none (a plugin, not a server) | **Stack:** Markdown skills, Python 3 stdlib hooks, Claude Code and Codex plugin manifests

## What
hsops is a Claude Code and Codex plugin of homeserver skills: setup, deploy, diagnose, monitor, back up, review (whole server, quick and changes), fix, learn and evolve. Users install it from the marketplace. Contributors develop it from a clone. Nothing here runs as a service.

## Quick Start

```bash
./setup.sh                    # Check python3, run the hook tests, print load commands
claude --plugin-dir .         # Load this clone in Claude Code (run from the repo root)
python3 -B tests/run.py       # Run the hook tests
```

## Commands

```bash
# Setup and loading
./setup.sh                                   # python3 check, hook tests, load instructions
claude --plugin-dir /path/to/hsops           # Load the clone in Claude Code
codex plugin marketplace add /path/to/hsops  # Add the clone as a Codex marketplace

# Testing
python3 -B tests/run.py                      # All hook tests (guard and evidence); run before a release

# Users install from GitHub (inside Claude Code)
/plugin marketplace add alexzfe/hsops
/plugin install hsops@hsops
```

No linter, coverage tool or build step is configured. Nothing needs compiling or installing.

## Architecture

```
.claude-plugin/     Claude Code manifests: plugin.json (version), marketplace.json
.codex-plugin/      Codex manifest: plugin.json
.agents/plugins/    Codex marketplace listing
skills/             One folder per skill, each with SKILL.md; review/, add-service/, fix/ and learn/ add references/
skills/evolve/      Turns repeated lessons into patterns, skill edits and new skills
agents/reviewer.md  The one generic reviewer agent: review, plan, verify and changes modes
hooks/              hooks.json wires guard.py and evidence.py into PreToolUse; _hook.py has shared helpers
shared/             conventions.md (fixed rules, data folder), learning-formats.md, profile-template.md, user-template.md
tests/              run.py (hook tests), guard-cases.txt (expected guard decision per command)
DESIGN.md           Why it is built this way. Read before restructuring.
ROADMAP.md          Ideas for later, each needing a design pass first
```

Skills are prompts that Claude follows, not code. The only executed code is the hooks (Python 3, stdlib only). At runtime, skills read and write the user's data in `~/.config/hsops/`, outside this repo. The guard hook checks disruptive server commands. The evidence hook checks writes to that data folder.

## Key Files

- `shared/conventions.md`: fixed rules every skill follows (data protection, server access, evidence)
- `shared/learning-formats.md`: the shapes of sightings, patterns and the ledger, and the rules for counts, cost and severe
- `skills/evolve/SKILL.md`: gathers lessons and the ledger, places each on the ladder, drafts, asks for approval, writes
- `hooks/guard.py`: `ask` for permanent data loss, deny-once for other disruptive commands
- `hooks/evidence.py`: first-write and hedge-word checks for data folder writes
- `hooks/_hook.py`: payload parsing, decisions, data folder path, per-session retry state
- `hooks/hooks.json`: wires both hooks into Claude Code
- `tests/run.py`: hook tests; `tests/guard-cases.txt`: the expected decision for each command
- `skills/review/SKILL.md`: the whole-server review flow; `skills/review/references/dimensions/`: the eight dimensions
- `skills/quick-review/SKILL.md`: the one-pass check with no agents; `skills/review-changes/SKILL.md`: the look at what a task changed
- `skills/fix/SKILL.md`: plan, approve, run one fix at a time, check after each
- `DESIGN.md`: the reasons behind the structure

## Configuration

hsops has no secrets and needs no configuration to run. Hooks read these from the process environment. They do not load `.env`, and `setup.sh` does not create one. See `.env.example`.

| Variable | Required | Description |
|----------|----------|-------------|
| `HSOPS_DATA_DIR` | No | Overrides the data folder. Default: `~/.config/hsops`. Read by `hooks/_hook.py`. |
| `CLAUDE_PLUGIN_DATA` | No | Folder for per-session hook retry state. Default: the system temp dir, under `hsops-hooks/`. |

## Rules for Changes

- Keep each `SKILL.md` under about 100 lines and each reference file under about 150. Split anything bigger.
- A skill's `description` starts with "Use when…" and lists triggers only, never the skill's steps (see DESIGN.md).
- No hostnames, IPs, usernames, personal paths or secrets in suite files, examples or tests.
- Add a line to `tests/guard-cases.txt` for every false alarm or miss you fix. Format: the expected decision (`ask`, `deny` or `allow`), then the command. Indented lines continue the command above.
- Hooks use only the Python standard library and must run under `python3 -B`. Tests need Python 3.7 or newer.
- Keep the four version fields equal when bumping: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`.
- Codex cannot return `ask`, so the test harness expects every `ask` to be a `deny` there.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
