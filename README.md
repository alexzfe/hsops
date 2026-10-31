# hsops

Homeserver operations for Claude Code and Codex. Take a mini PC, an old laptop or a Raspberry Pi from bare hardware to a running server. Deploy apps, diagnose problems, set up monitoring and backups, and get in-depth reviews. hsops learns from every session.

## Install

**Claude Code**
```
/plugin marketplace add alexzfe/hsops
/plugin install hsops@hsops
```

**Codex**
```bash
codex plugin marketplace add alexzfe/hsops
codex plugin add hsops@hsops
```

**Developing hsops:** run it from your clone with `claude --plugin-dir /path/to/hsops`, or `codex plugin marketplace add /path/to/hsops`. In a clone, `/hsops:learn` writes general lessons straight into the suite.

## Skills

| Skill | What it does |
|---|---|
| `/hsops:setup` | Starts from bare hardware, a fresh OS or an existing server, and covers OS install, hardware checks, SSH, remote access, Docker, storage and choosing apps. |
| `/hsops:add-service` | Deploys and updates apps with Docker Compose. |
| `/hsops:diagnose` | Works from the symptom to an evidence-backed root cause and fix. |
| `/hsops:monitoring` | Sets up alerts that reach you, and tests every one. |
| `/hsops:backups` | Local and off-site copies, finished only once a test restore succeeds. |
| `/hsops:review` | An in-depth review across eight dimensions, run as parallel reviewers in Claude Code and ranked by your priorities. |
| `/hsops:fix` | Carries out review recommendations: a plan for each, one approval, then one fix at a time with a check after each. |
| `/hsops:learn` | Turns a session's surprises into lasting knowledge. |

hsops doesn't push a fixed stack. It asks about your needs and priorities, lays out the options with their tradeoffs, recommends one, and works with whatever you choose. A short list of fixed rules (in `shared/conventions.md`) protects your data and your access to the server.

## Hooks

hsops ships two hooks that back up its rules. They need `python3` on your workstation.

The **guard hook** watches disruptive commands, both on the server (inside `ssh`) and on block devices on your workstation:

- **Commands that destroy data** (`mkfs`, `wipefs`, `dd` to a device, `zfs destroy`, `docker volume rm`, `rm -r` on data paths) show you a confirmation prompt with the exact command.
- **Other disruptive commands** (restarts, reboots, `docker compose down`, firewall and sshd changes, package removal) are stopped once, until Claude has shown your go-ahead and the rollback; the identical command then runs.

To turn it off for one server, add `guard: off` to that server's `profile.md`.

The **evidence hook** keeps guesses out of `~/.config/hsops/`. The first write to each file in a session is sent back once, so Claude names the evidence for each line (your own words, for a preference), and so is any write with hedged lines such as "probably" or "not verified".

In Codex, hooks can't ask yet, so the guard stops every match once instead of prompting you. Codex also asks you to trust the plugin's hooks once, in `/hooks`.

## Your data

Everything hsops learns about you and your servers stays on your machine in `~/.config/hsops/`:

```
user.md                    your experience level and preferences
general/<skill>.md         general lessons from your sessions
servers/<name>/
  profile.md               hardware, layout, services, priorities
  lessons.md               this server's quirks
  changelog.md             every change made
  reviews/                 past reviews and the status of each recommendation
```

Setup offers to make this folder a git repo. hsops runs on your workstation and reaches the server over SSH. It was designed with Herdr (a terminal multiplexer for coding agents) in mind, and works without it.

## Contributing

When `/hsops:learn` finds a lesson that would help everyone, it offers to draft an issue or PR here. Run `python3 tests/run.py` before a release, and add a line to `tests/guard-cases.txt` for every false alarm or miss reported. Keep each SKILL.md under about 100 lines and each reference file under about 150; anything bigger should be split into its own file. Ideas planned for later are in [ROADMAP.md](ROADMAP.md). The reasons behind the structure are in [DESIGN.md](DESIGN.md).

For setup, the pull request workflow and issue guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md). In a clone, `./setup.sh` runs the tests and prints how to load the plugin. [CLAUDE.md](CLAUDE.md) has the commands and architecture for contributors.

## License

MIT. See [LICENSE](LICENSE).
