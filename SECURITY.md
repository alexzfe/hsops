# Security

hsops runs commands on people's servers, so I want to hear about security problems.

## Reporting a problem

Report it privately through [GitHub's vulnerability reporting](https://github.com/alexzfe/hsops/security/advisories/new). Do not open a public issue.

Include the hsops version, what you ran and what happened. Remove hostnames, IP addresses, usernames and secrets first.

hsops is a hobby project, so I can't promise a response time. Fixes go into the latest version only.

## What counts

Report these privately:

- a way for untrusted content, such as a file or command output on a server, to get a destructive command past the guard hook
- a skill or hook that exposes secrets or writes them to the data folder or the suite
- a skill's instructions that weaken a server's security without telling the user.

An ordinary false alarm or miss from the guard or evidence hook can go in a public issue, using the steps in [CONTRIBUTING.md](CONTRIBUTING.md).

## What the hooks don't do

The hooks are guardrails, not a security boundary. They catch a model that drifts from the rules, and only the `ask` tier puts the decision in front of a person. Deny-once can't stop a model that wrongly believes it has your approval (see [DESIGN.md](DESIGN.md)). Setting `guard: off` in a server's profile turns the guard off for that server. In Codex, every match is deny-once.
