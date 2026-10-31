# hsops

hsops is a suite of skills and hooks for Claude Code and Codex that helps you set up, manage and maintain your own self-hosted server. Take a mini PC, an old laptop or a Raspberry Pi from bare hardware to a running server, then deploy apps, diagnose problems, set up monitoring and backups, and get in-depth reviews. hsops keeps notes on your server between sessions and stops before commands that could destroy your data.

## Why use hsops?

| Asking an agent directly | With hsops |
|---|---|
| "Be careful" is an instruction it can forget | A hook stops disruptive commands until Claude has shown your go-ahead, and commands that destroy data prompt you directly (in Claude Code) |
| A backup looks done once it has run | A backup is finished only after a test restore succeeds and a missed run has raised an alert |
| Each session starts by rediscovering your server | Each session starts by reading your server's profile, lessons and changelog |
| A guess can get saved as a fact | A hook sends notes back until Claude names the evidence for them |
| You get whatever stack it suggests | It asks about your needs, lays out the options with their tradeoffs and recommends one, and your choice is final |

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

## Getting started

Run `/hsops:setup`, or tell your agent you want to set up a homeserver. It asks about your experience level, how much it may change without asking, and where you're starting from: bare hardware, a fresh OS or an existing server. On an existing server, it records what's already there and changes only what you ask for.

From there it works through hardware checks, SSH, remote access, Docker, storage and choosing apps, and each step ends on a check. You finish with a summary of what's running and how to reach it, and a recommendation for what to set up next.

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

## Background

I'm a hobbyist, and I've greatly enjoyed running a homeserver. It's convenient, it's fun, and I've learned a lot from it. I built hsops to help other people get the same out of theirs, and I think it can help people who are new to self-hosting step into that world.

I drew inspiration from Louis Rossmann and his longform guides to self-hosting: the [video guide](https://www.youtube.com/watch?v=Et5PPMYuOc8) and the [text guide](https://wiki.futo.org/index.php/Introduction_to_a_Self_Managed_Life:_a_13_hour_%26_28_minute_presentation_by_FUTO_software).

## Contributing

When `/hsops:learn` finds a lesson that would help everyone, it offers to draft an issue or PR here. Run `python3 tests/run.py` before a release, and add a line to `tests/guard-cases.txt` for every false alarm or miss reported. Keep each SKILL.md under about 100 lines and each reference file under about 150; anything bigger should be split into its own file. Ideas planned for later are in [ROADMAP.md](ROADMAP.md). The reasons behind the structure are in [DESIGN.md](DESIGN.md).

For setup, the pull request workflow and issue guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md). In a clone, `./setup.sh` runs the tests and prints how to load the plugin. [CLAUDE.md](CLAUDE.md) has the commands and architecture for contributors. To report a security problem, see [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
