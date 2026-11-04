# Learn and Evolve Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lessons build up with counted occurrences and cost, grow into patterns, skill edits, safety edits and new skills, through a changed `learn` and a new `evolve` skill.

**Architecture:** `learn` captures per session (lessons, sightings, skill edits, ledger entries). `evolve` consolidates on request (promotions, patterns, new skills, safety edits, prunes). The formats both share live in one file under `shared/`. The only code change is the evidence hook's per-file questions.

**Tech Stack:** Markdown skills; Python 3.7+ stdlib hook (`hooks/evidence.py`), run under `python3 -B`.

**Spec:** `docs/superpowers/specs/2026-11-03-learn-evolve-design.md`

## Global Constraints

- Each `SKILL.md` under about 100 lines; each reference or shared file under about 150.
- A skill's `description` starts with "Use when…" and lists triggers only, never steps.
- No hostnames, IPs, usernames, personal paths or secrets in suite files, examples or tests. Use `<server>` and `myserver`.
- Hooks use only the Python standard library and run under `python3 -B`.
- Version 0.6.0 in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` and `CLAUDE.md`.
- Every line written to the data folder rests on evidence (conventions: Evidence). Cost is measured in the session; it is never estimated.
- Skills follow the shape of existing ones: read `../../shared/conventions.md` first, numbered stages, a `**Done when:**` per stage.

## Review Focus

1. **The same occurrence counted twice.** Learn run twice in one session, or a review item that shows up again in fix, must not add a second occurrence. Rule in `shared/learning-formats.md`: an occurrence is keyed by date plus its event (the review item or the command), and an existing key isn't added again. Task 2 pins it.
2. **Machine details leaking upward.** A promoted lesson or a pattern carrying a hostname, IP, drive serial or personal path. The content test in `learn/references/routing.md` and evolve's Draft stage must strip them, and the split keeps the specifics in `lessons.md`. Tasks 3 and 4 pin it.
3. **Knowledge lost when a pattern absorbs lessons.** Evolve removes a general lesson only when its whole content, condition included, appears in the pattern; otherwise it stays. Task 4 pins it.
4. **A plugin user's evolve writing to the read-only cache.** Evolve uses learn's maintainer-mode test, so on a plugin install, skill edits and new skills become upstream drafts. Task 4 pins it.
5. **Missing files on a first run.** No `candidates.md`, no `general/patterns/`, an empty `general/`. Learn and evolve create a file only when they have an approved entry to write, and treat a missing file as empty. Tasks 3 and 4 pin it.

---

### Task 1: Evidence hook questions for patterns and the ledger

**Files:**
- Modify: `hooks/evidence.py` (`QUESTIONS`, `file_class`)
- Test: `tests/run.py` (`run`, `test_evidence`)

**Interfaces:**
- Produces: `file_class(path) -> str`, returning one of `"user"`, `"pattern"`, `"ledger"`, `"general"`, `"server"`. `QUESTIONS` gains `"pattern"` and `"ledger"` keys.

- [ ] **Step 1: Write the failing tests**

In `tests/run.py`, give `run()` a `reason=False` keyword. When true, return `permissionDecisionReason` (or `""` on allow) instead of the decision. Add to `test_evidence`:

```python
pattern = os.path.join(data, "general", "patterns", "monitoring", "smart-selftests.md")
ledger = os.path.join(data, "general", "candidates.md")
p_plain = {"file_path": pattern, "content": "# SMART self-tests\nWhen: scheduling self-tests.\n"}
expect("evidence: first write to a pattern asks for pitfall events",
       "each pitfall" in run(tmp, "evidence.py", "Write", p_plain, "evp", reason=True), True)
expect("evidence: first write to the ledger asks for each occurrence",
       "each occurrence" in run(tmp, "evidence.py", "Write", {"file_path": ledger, "content": "## Skill: x\n"}, "evl", reason=True), True)
expect("evidence: a hedged pattern line",
       run(tmp, "evidence.py", "Edit", {"file_path": pattern, "old_string": "", "new_string": "Pitfalls: NVMe probably needs a flag.\n"}, "evp"), "deny")
expect("evidence: a sighting tag is not a hedge",
       run(tmp, "evidence.py", "Edit", {"file_path": lessons, "old_string": "4 GB of RAM.", "new_string": "4 GB of RAM. (seen 2026-11-01, 2026-11-03 ×2)"}, "ev"), "allow")
expect("evidence: other general files keep the lesson question",
       "beyond this one server" in run(tmp, "evidence.py", "Write", {"file_path": os.path.join(data, "general", "fix.md"), "content": "- x\n"}, "evg", reason=True), True)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -B tests/run.py`
Expected: `FAIL evidence: first write to a pattern asks for pitfall events` and `FAIL evidence: first write to the ledger asks for each occurrence`. The others pass already.

- [ ] **Step 3: Implement**

In `file_class`, check `general/patterns/` (any depth) → `"pattern"`, `general/candidates.md` → `"ledger"`, before the existing `general` test. Add the copy:

```python
"pattern": "the session events behind each pitfall (a command and its output), the check you ran and its output, "
           "and confirm no line names this server's hosts, IPs, paths or hardware serials.",
"ledger": "for each occurrence, the user's words or the review item, its date, and its cost as measured this session; "
          "for a Severe line, the event that put data or access at risk.",
```

Update the module docstring's first bullet to say the questions differ for lessons, patterns, the ledger, `user.md` and server files.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -B tests/run.py`
Expected: `all hook tests passed`

- [ ] **Step 5: Commit**

```bash
git add hooks/evidence.py tests/run.py
git commit -m "feat(evidence): own first-write questions for patterns and the ledger"
```

### Task 2: Shared learning formats and conventions

**Files:**
- Create: `shared/learning-formats.md`
- Modify: `shared/conventions.md` (Data folder; Load context first)

**Interfaces:**
- Produces: the file both skills read for these formats: the sighting tag, occurrences, `Cost:` and `Severe:`, the pattern shape, the ledger entry, readiness and declines. Section headings, exactly: `## Sightings`, `## Occurrences`, `## Cost and severe`, `## Patterns`, `## Ledger`, `## Ready and declined`.

- [ ] **Step 1: Write `shared/learning-formats.md`**

Content from the spec's "Data shapes" section, with the spec's examples (generic, `<server>`). Add the Review Focus 1 rule under `## Occurrences`: *an occurrence is keyed by its date and its event (the review item, or the command and its output); a key already recorded is not added again, so a second learn run in the same session adds nothing.* Under `## Cost and severe`, keep the line "skills streamline; checks make things safe", and note that `Severe` makes only a safety edit eligible.

- [ ] **Step 2: Update `shared/conventions.md`**

- In **Data folder**, under `general/`, add `general/patterns/<skill>/<topic>.md` (multi-step recipes) and `general/candidates.md` (the ledger), each pointing to `shared/learning-formats.md`.
- In **Load context first**, add this bullet: "this skill's patterns: list `references/patterns/` in the skill's directory and `general/patterns/<skill>/` in the data folder, and read any whose name matches the task".

- [ ] **Step 3: Verify**

Run: `wc -l shared/learning-formats.md shared/conventions.md && grep -n "patterns" shared/conventions.md && grep -rnE "([0-9]{1,3}\.){3}[0-9]{1,3}" shared/learning-formats.md`
Expected: `learning-formats.md` under 150 lines. Both conventions lines are present. The IP grep prints nothing.

- [ ] **Step 4: Commit**

```bash
git add shared/learning-formats.md shared/conventions.md
git commit -m "feat: shared learning formats; skills load their patterns"
```

### Task 3: `learn` captures sightings, skill edits and ledger entries

**Files:**
- Modify: `skills/learn/SKILL.md`
- Create: `skills/learn/references/routing.md`

**Interfaces:**
- Consumes: `shared/learning-formats.md` (Task 2).
- Produces: the evolve pointer line, exactly: `Ready for /hsops:evolve: <entries>`. Learn's maintainer-mode test lives in `references/routing.md` under `## Maintainer mode`, and evolve reuses it.

- [ ] **Step 1: Move routing into `references/routing.md`**

Headings: `## Content test` (software behavior → general; this machine's paths, hardware, layout or choices → `lessons.md`; mixed → split, the general part with its condition; strip hostnames, IPs, serials and personal paths from anything general), `## Destinations` (today's table, with the "Unsure → lessons.md" row removed and rows added for skill edits and ledger entries), and `## Maintainer mode` (today's rule, extended so any `SKILL.md`, reference or `conventions.md` counts; plugin users get upstream drafts).

- [ ] **Step 2: Rewrite `skills/learn/SKILL.md` stages**

- Read `../../shared/conventions.md` and `../../shared/learning-formats.md` first.
- **1. Harvest:** today's list, plus sightings, skill-edit candidates (each naming its event) and skill candidates. Each candidate records its `Cost:`, and `Severe:` when data or access was at risk. A severe candidate also becomes a ledger safety edit.
- **2. Route:** point to `references/routing.md`. A missing target file is treated as empty and created only on an approved write.
- **3. Refine** and **4. Approve:** as today. The brief adds sightings, skill edits and ledger entries, and shows each lesson's general-or-server pick.
- **5. Upstream:** unchanged.
- Remove **6. Prune**, which now belongs to evolve. Add a closing step: when the ledger has a ready entry (`shared/learning-formats.md`, `## Ready and declined`) or 3 or more lessons share a topic within one skill's job, end with `Ready for /hsops:evolve: …` in one line.
- **Done when:** every harvested candidate has been written, logged, shared or declined.
- Description: add "or to record that a lesson came up again" to the triggers. Keep it trigger-only.

- [ ] **Step 3: Verify**

Run: `wc -l skills/learn/SKILL.md skills/learn/references/routing.md && head -3 skills/learn/SKILL.md && grep -n "Prune\|Unsure" skills/learn/SKILL.md skills/learn/references/routing.md`
Expected: under 100 and 150 lines. The description starts `Use when`. The last grep prints nothing.

- [ ] **Step 4: Read-through**

Read the new `SKILL.md` top to bottom, imagining this session's SMART work as the input. Check that it would record an occurrence on the existing NVMe lesson instead of writing a new line, and would send the namespace rule up with its condition while keeping the drive model on the server.

- [ ] **Step 5: Commit**

```bash
git add skills/learn
git commit -m "feat(learn): sightings, cost, content test, skill edits, ledger, evolve pointer"
```

### Task 4: The `evolve` skill

**Files:**
- Create: `skills/evolve/SKILL.md`

**Interfaces:**
- Consumes: `shared/learning-formats.md` (Task 2); `skills/learn/references/routing.md` `## Content test` and `## Maintainer mode` (Task 3); `agents/reviewer.md` in **review** mode, for a new-skill draft.

- [ ] **Step 1: Write `skills/evolve/SKILL.md`**

Frontmatter description, exactly: `Use when the user runs /hsops:evolve, asks to turn lessons into patterns or new skills, or when learn reports entries ready for evolve.`

Stages from the spec's "The evolve skill" section: **1. Gather**, **2. Place**, **3. Order**, **4. Draft**, **5. Approve**, **6. Write and record**, each with a `**Done when:**`. Include:
- In Gather: missing files count as empty (Review Focus 5).
- In Place: the trigger test in writing. Safety edits go where they prevent the problem, never into a new skill.
- In Order: safety edits first, then cost × occurrences.
- In Draft:
  - Remove a general lesson only when the pattern holds its whole content and condition; otherwise keep it (Review Focus 3).
  - Strip machine details (Review Focus 2).
  - New skills model on an existing skill of the same kind.
  - One `hsops:reviewer` pass per new-skill draft.
  - Use the Maintainer mode test from learn's routing file (Review Focus 4).
- In Write: ledger `built: <path>` or `Declined YYYY-MM-DD: "<reason>"`. On a clone: the `CLAUDE.md` architecture line, the four version fields, a branch and a PR.

- [ ] **Step 2: Verify**

Run: `wc -l skills/evolve/SKILL.md && head -3 skills/evolve/SKILL.md && grep -c "Done when" skills/evolve/SKILL.md`
Expected: under 100 lines. The description is exactly as above. The count is 6 or more.

- [ ] **Step 3: Read-through against real data**

Read the skill against `~/.config/hsops/servers/*/lessons.md` (read only, change nothing). Write down in the commit body what it would propose. It must match the spec's evolve acceptance list: the four software-behavior promotions, three lessons kept, the NVMe split, a SMART pattern under `monitoring` and not a skill, and secret rotation as a skill candidate with a separate safety edit for secrets in git.

- [ ] **Step 4: Commit**

```bash
git add skills/evolve
git commit -m "feat: evolve skill consolidates lessons into patterns, skill edits and new skills"
```

### Task 5: Docs and version

**Files:**
- Modify: `DESIGN.md`, `CLAUDE.md`, `README.md`, the four manifests

- [ ] **Step 1: `DESIGN.md` decision entry**

Write it in the file's existing Decision / Why shape. Cover:
- the ladder
- counts as eligibility and cost as order
- skills streamline while checks make things safe, so `Severe` leads only to safety edits
- no time decay
- declines that reopen on new occurrences
- no passive observer, because of the evidence rule and secrets in logs

- [ ] **Step 2: `CLAUDE.md` and `README.md`**

- `CLAUDE.md`, Architecture: add `evolve/` and `learn/references/`, and list `shared/learning-formats.md` under `shared/`.
- `CLAUDE.md`, Key Files: add `skills/evolve/SKILL.md` and `shared/learning-formats.md`.
- `README.md`, skills table: add a `/hsops:evolve` row, "Turns repeated lessons into patterns, skill improvements and new skills."
- `README.md`, the Developing note: mention that learn and evolve write into the suite on a clone.

- [ ] **Step 3: Version 0.6.0**

Run: `sed -i 's/"version": "0.5.0"/"version": "0.6.0"/' .claude-plugin/plugin.json .claude-plugin/marketplace.json .codex-plugin/plugin.json .agents/plugins/marketplace.json && sed -i 's/^\*\*Version:\*\* 0.5.0/**Version:** 0.6.0/' CLAUDE.md && grep -rn '"version"\|\*\*Version' .claude-plugin .codex-plugin .agents CLAUDE.md`
Expected: five lines, all showing 0.6.0.

- [ ] **Step 4: Final verification**

Run: `python3 -B tests/run.py && wc -l skills/*/SKILL.md | sort -n | tail -3`
Expected: `all hook tests passed`, and no `SKILL.md` over about 100 lines.

- [ ] **Step 5: Commit and open the PR**

```bash
git add DESIGN.md CLAUDE.md README.md .claude-plugin .codex-plugin .agents
git commit -m "docs: learn and evolve design decision, README and version 0.6.0"
git push -u origin learn-evolve
gh pr create --title "Learn and evolve: lessons into patterns and skills" --body "<summary; links the spec; lists the two acceptance runs left for after merge>"
```

## After merge: acceptance on real data

Run by the user, not part of the implementation:
1. `/hsops:learn` at the end of a homeserver session, checked against the spec's learn acceptance list.
2. `/hsops:evolve`, checked against the spec's evolve acceptance list.
