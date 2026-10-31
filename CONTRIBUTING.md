# Contributing to hsops

Thanks for helping. hsops is a set of skills and two Python hooks for Claude Code and Codex. Most changes are Markdown, so the bar is clarity, accuracy and safety for people's servers.

## Development setup

You need `python3` 3.7 or newer. Nothing else is required.

```bash
git clone https://github.com/alexzfe/hsops.git
cd hsops
./setup.sh
```

`setup.sh` checks `python3`, runs the hook tests and prints how to load the plugin from your clone:

```bash
claude --plugin-dir /path/to/hsops          # Claude Code
codex plugin marketplace add /path/to/hsops # Codex
```

Read [CLAUDE.md](CLAUDE.md) for the commands and architecture, and [DESIGN.md](DESIGN.md) before restructuring anything.

## Running the tests

```bash
python3 -B tests/run.py
```

The tests cover the guard and evidence hooks. They use a temporary data folder, so they never touch your `~/.config/hsops/`. All tests must pass before you open a pull request. Run them again before any release.

## Branches and pull requests

- Branch from `main`, and keep each pull request to one change.
- Open pull requests against `main`.
- Describe what changed and why. For a behavior change, say how you checked it (the command you ran and its output).
- If a change affects a guard or evidence decision, add the case to `tests/guard-cases.txt` in the same pull request.
- Keep the four version fields equal when a release bumps the version (see CLAUDE.md).

## Style notes

- **Skills are instructions.** Write `SKILL.md` files as steps Claude can follow. Say what to check, what to ask the user and what never to do.
- **Keep files short.** `SKILL.md` under about 100 lines, reference files under about 150. Split bigger content into its own file.
- **No personal or server data.** Never commit hostnames, IP addresses, usernames, personal paths, emails, tokens or session logs. Examples should use placeholders such as `myserver` or `/srv/media`.
- **Hooks use only the standard library.** They run as `python3 -B`, and their output must be the JSON decision the tests expect.
- **Fixed rules are in `shared/conventions.md`.** They protect the user's data and their access to the server. A change to a fixed rule needs a clear reason in the pull request.
- **Match the existing voice.** Plain, direct sentences. No marketing language.

## Reporting issues

Use the issue templates:

- **Bug report:** what you ran, what you expected, what happened, and your environment (hsops version, Claude Code or Codex version, workstation OS, server OS).
- **Feature request:** the problem you are solving, and how you would like it to work.

Before you post, remove anything private from logs and output: hostnames, IP addresses, usernames, paths under your home folder and any secrets. If the guard or evidence hook gave a wrong decision, paste the command (redacted) and the decision you expected. That case can go into `tests/guard-cases.txt`.

Do not post security problems in a public issue. Report them privately instead, as described in [SECURITY.md](SECURITY.md).

## Using Claude Code

This repository includes a `CLAUDE.md` that gives Claude Code the commands, architecture and rules for working on hsops. From the repo root:

```bash
claude --plugin-dir .
```

Claude Code reads `CLAUDE.md` automatically. Use `/hsops:learn` in a clone to write general lessons straight into the suite. Review every edit with `git diff` before you commit.

## License

By contributing, you agree that your contributions are licensed under the MIT License in [LICENSE](LICENSE).
