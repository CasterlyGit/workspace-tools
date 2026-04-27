# Agentic workspace — full inventory & cheat sheet

A personal, mostly-local SDD pipeline that turns a voice idea or GitHub issue into committed code via a chained set of skills. GitHub Issues + Projects v2 is the data layer. `~/Documents/Dev/<project>/` is where the code lives. `.flow/<task-id>/` inside each repo holds the spec artifacts. `~/Documents/ObsidianVault/Specs/` aggregates them for browsing in Obsidian (or any markdown editor).

**Last updated:** 2026-04-26 (workspace-tools orchestrator now lives at `~/Documents/Dev/workspace-tools/`).

## ⚡ Resume context for a fresh session

Pick up exactly here by reading this file end-to-end + the workspace-tools README + checking live state. The most recent active work is the **live-progress + finer granularity** improvement to the orchestrator-status integration.

**Where we are right now:**

| Layer | Status |
|---|---|
| Inbox flow (markdown ticket → click `go` → agent) | ✅ Working. Buttons in `_status.md` trigger via `inbox-process.sh --go`. |
| Orchestrator (Python, replaces brittle markdown `/iterate`) | ✅ Built at `~/Documents/Dev/workspace-tools/`. Pushed to [GitHub](https://github.com/CasterlyGit/workspace-tools). 21 files. Has `Agent`, `Pipeline`, `Stage`, `StateSink`, 7 stages, multiple pipeline shapes (`full` / `bugfix` / `quickfix`), CLI with `--shape` flag, deterministic stage progression. |
| Live status from orchestrator → `_status.md` | 🟡 Wired but **per-stage only**. The user wants finer granularity ("more sensitivity in the progress bar type") — sub-stage breadcrumbs that update as the agent uses tools mid-stage. Not yet implemented. |
| Smoke test on issue #13 (hover bug) | ❌ Not yet — test killed mid-run when we pivoted. |
| Old `_pipeline:*` skills + `_archive:*` | Still present, no longer load-bearing. The new `iterate.md` shells out to `python -m workspace_tools.cli iterate "$ARGUMENTS"`. |

**What the next session should do (in order):**

1. **Fix sub-stage progress granularity.** In `~/Documents/Dev/workspace-tools/workspace_tools/core/state_sink.py`, add a method `note_activity(line: str)` that updates a `last_activity` field on the ticket entry (truncated, rolling). Wire it into `PipelineHooks.on_agent_line` in `cli.py`. Update the renderer in `~/bin/inbox-process.sh` (look for the `current_stage` block) to display `state.last_activity` under the stage progress as a one-line breadcrumb. Throttle updates to once every ~2s so we don't write the JSON on every token.
2. **Smoke-test on curby issue #13** — `python -m workspace_tools.cli iterate https://github.com/CasterlyGit/curby/issues/13 --shape bugfix` from inside `~/Documents/Dev/workspace-tools/`. Watch `_status.md` update live in Obsidian — should show 🟢 #13 · design (3/5) · _bugfix_ · "<last activity line>" advancing.
3. **Branch reuse for resume across slug changes.** Already partially landed in cli.py — verify it picks up `auto/13-dock-puck-hover-stability` (the leftover branch) when re-running on issue #13. If not, fix.
4. **Commit + push improvements** to workspace-tools.

**Gotchas to remember:**

- Bash `IFS=$'\t'` collapses consecutive tabs in `read`. Use `\x1f` (unit separator) or non-empty placeholders. Already fixed in `inbox-process.sh`.
- macOS LaunchAgents can't read `~/Documents/`. The watcher auto-starts from `~/.zshrc` instead.
- `gh repo create` after `git init` works but `gh project create` returns the project NUMBER as `.number` (not `.id`).
- The orchestrator runs `claude --print` per stage. Each is a fresh subprocess; they don't share conversation. Spec artifacts on disk are the only handoff.

---

## TL;DR — daily commands

| Want to | Run |
|---|---|
| Build a brand-new project from an idea | `/automate "<idea>"` |
| Work the next issue (top of "Up Next" on the hub) | `/iterate next` |
| Work a specific issue | `/iterate <issue-url>` |
| File an issue fast | `/file feature curby — <title>` |
| Bring an existing repo into the system | `/onboard <owner>/<repo>` |
| Bootstrap or refresh the master Workspace project | `/hub` |
| Apply standard labels to a repo | `/label-sync <owner>/<repo>` |
| Apply standard board kit to a project | `/board-setup <project-number>` |
| Run a single pipeline stage manually | `/_pipeline:explore`, `/_pipeline:design`, etc. |

---

## Live state (2026-04-26)

### Repos onboarded
| Repo | Local | Project board |
|---|---|---|
| [`CasterlyGit/curby`](https://github.com/CasterlyGit/curby) | `~/Documents/Dev/curby/` | [#2 curby](https://github.com/users/CasterlyGit/projects/2) |
| [`CasterlyGit/neon-stereo`](https://github.com/CasterlyGit/neon-stereo) | `~/Documents/Dev/neon-stereo/` | [#1 neon-stereo](https://github.com/users/CasterlyGit/projects/1) |

### Hub
**[Workspace #3](https://github.com/users/CasterlyGit/projects/3)** — aggregates issues from every onboarded repo. Default view: Backlog → Up Next → In Progress → In Review → Done. Priority + Target fields available on every item.

### Open work (filed via `/file` during this session)
- curby#2 — Agent system prompt: inject user-environment context (`feature` `priority:p1`)
- curby#3 — Status puck shows the final response twice (`bug` `polish` `priority:p3`)
- curby#4 — Voice indicator off-screen after monitor disconnect (`bug` `priority:p2`)
- curby#5 — Better startup affordance for voice indicator (`feature` `polish` `priority:p2`)
- neon-stereo#1–7 — Manual verification checks for v0.1
- neon-stereo#8 — v0.2: macOS DMG packaging via electron-forge

---

## Architecture

```
~/.claude/commands/
├── _README.md            ← this file
├── _archive/             ← old Spec Kit skills (preserved, ignore)
├── _labels.json          ← standard label kit
├── _board-kit.json       ← standard Project field kit
│
├── automate.md          /automate "<idea>"             — greenfield: new repo + project + MVP
├── iterate.md           /iterate <issue-url|next>      — brownfield: branch + PR
├── onboard.md           /onboard <owner>/<repo>        — bring an existing repo into the system
├── hub.md               /hub                           — bootstrap the master Workspace project
├── label-sync.md        /label-sync <owner>/<repo>    — apply label kit to a repo
├── board-setup.md       /board-setup <project>         — apply field kit to a project
├── file.md              /file <args>                   — quick issue creation
│
├── _pipeline/            ← stages, called by orchestrators (also runnable directly)
│   ├── explore.md       /_pipeline:explore
│   ├── research.md      /_pipeline:research
│   ├── requirements.md  /_pipeline:requirements
│   ├── design.md        /_pipeline:design
│   ├── test-plan.md     /_pipeline:test-plan
│   ├── implement.md     /_pipeline:implement
│   └── integration-test.md /_pipeline:integration-test
│
└── _templates/
    ├── REQUIREMENTS.md.tmpl
    ├── DESIGN.md.tmpl
    ├── TEST_PLAN.md.tmpl
    ├── INTEGRATION.md.tmpl
    ├── ISSUE_BUG.yml      ← drops into <repo>/.github/ISSUE_TEMPLATE/
    └── ISSUE_FEATURE.yml
```

## Per-task artifact layout

When `/iterate` runs against an issue, or `/automate` builds a new project, every stage writes one Markdown artifact under:

```
<repo>/.flow/<task-id>/
├── EXPLORE.md           ← stage 1 (skipped on greenfield init)
├── RESEARCH.md          ← stage 2
├── REQUIREMENTS.md      ← stage 3
├── DESIGN.md            ← stage 4
├── TEST_PLAN.md         ← stage 5
├── IMPLEMENTATION.log   ← stage 6 (commit list + deviations)
└── INTEGRATION.md       ← stage 7 (AC verification + decision)
```

`<task-id>` is `init` for greenfield projects, or `issue-<N>` for brownfield iterations.

## Pipeline contract

```
EXPLORE → RESEARCH → REQUIREMENTS → DESIGN → TEST_PLAN → IMPLEMENTATION → INTEGRATION
                                       ↓
                              (each stage reads everything before it)
```

Each stage:
- Reads a known set of prior artifacts.
- Writes exactly one artifact under `.flow/<task-id>/`.
- Is committed on its own git commit (so the PR diff shows progression).
- Stops if the prior artifact is missing — no improvising.

## Standard label kit

Applied to every repo by `/label-sync` (also runs inside `/onboard` and `/automate`):

| Type | Labels |
|---|---|
| Type | `bug` `feature` `polish` `chore` `docs` `security` |
| Priority | `priority:p0` `priority:p1` `priority:p2` `priority:p3` |
| State | `blocker` `manual-verification` `ready-for-review` `wip` `auto-generated` `needs-info` |

Existing labels not in the kit are preserved (never deleted).

## Standard board kit

Applied to every Project v2 by `/board-setup` (also runs inside `/onboard`, `/automate`, `/hub`):

| Field | Type | Options |
|---|---|---|
| Status | single-select | Backlog · Up Next · In Progress · In Review · Done |
| Priority | single-select | P0 · P1 · P2 · P3 |
| Target | text | free-form (e.g. `v0.2`, `Q3 2026`) |

The default `Todo / In Progress / Done` Status options get replaced by the kit's via GraphQL `updateProjectV2Field`.

## Obsidian vault — your local Jira

All project specs are symlinked into `~/Documents/ObsidianVault/Specs/<project>/`. Open Obsidian on `~/Documents/ObsidianVault/` and you can search across every project's REQUIREMENTS / DESIGN / etc. in one place. The symlinks point at live `.flow/` dirs in each repo — edits in either location reflect in both.

### File-as-ticket workflow (gated approval)

A background watcher (`~/bin/inbox-watcher.sh`, auto-started from `~/.zshrc`) turns markdown files into GitHub issues — but only when you explicitly approve. Three states:

| State | What happens | How you get there |
|---|---|---|
| **draft** | File registered. Shows up in `Specs/_status.md` under "Drafts". **No GitHub action taken.** | Create the file. |
| **filed** | Issue created on GitHub, added to repo project + Workspace hub, `/iterate` kicks off via `claude --print`. | Add `approve: yes` to the file and save. |
| **closed** | Issue auto-closed with "marked done by user". State entry removed. | Delete the file. |

The status file at `~/Documents/ObsidianVault/Specs/_status.md` is auto-regenerated after every event with two columns:
- **Drafts** — waiting for your approval.
- **Filed** — issue open, `/iterate` may be running.

### Magic lines (optional, anywhere in the first 10 lines)

```
approve: yes       # default: no. THE GATE — set yes to actually file the issue.
type: bug          # default: feature. valid: bug | feature | polish | chore | docs | security
priority: p1       # default: none. valid: p0 | p1 | p2 | p3
auto-iterate: no   # default: yes. set "no" to file the issue but skip running /iterate
```

A first-line `# Heading` overrides the filename as the title.

### Per-repo state

Each repo has `<repo>/inbox/.state.json` mapping ticket filenames to their status + issue URL + title. This is local-only (gitignored) — the canonical record is on GitHub.

### Watcher pieces

- `~/bin/sync-vault.sh` — refresh the vault symlinks for newly onboarded repos
- `~/bin/inbox-process.sh` — handle one note (file or close)
- `~/bin/inbox-watcher.sh` — fswatch loop, calls process per event
- `~/.zshrc` snippet — auto-starts the watcher when you open a Terminal (a launchd LaunchAgent was tried but blocked by macOS TCC on `~/Documents/`; running from your shell context inherits the right permissions)
- Logs: `/tmp/inbox.log` (events), `/tmp/inbox-iterate.log` (claude pipeline runs), `/tmp/inbox-watcher.log` (watcher itself)

## Decisions locked in

- **Workspace** — `~/Documents/Dev/<project>/` for code, `~/Documents/ObsidianVault/Specs/<project>/` for spec browsing.
- **Project = repo.** Greenfield (`/automate`) creates a new repo + Project. Brownfield (`/iterate`) branches + PRs.
- **Pickup default** — `/iterate next` reads the top of the hub's "Up Next" column.
- **Pause points** — automatic end-to-end; the human gate is the PR review for brownfield, and the integration report for greenfield.
- **Permissions** — `defaultMode: bypassPermissions` set in `~/.claude/settings.json`. `Bash(git commit*)` is the only deny rule (safety net — say the word to drop it).

---

## Resume in a fresh session

If you restart Claude Code mid-flight, paste:

```
Read ~/.claude/commands/_README.md and tell me where we are.
```

I'll re-read this file plus inspect the live state (`gh repo list`, `gh project list`, `git status` per repo) and pick up.

## Things still open (record here as decisions land)

- `CasterlyGit/curby-stub` — leftover empty repo from the rename. Delete manually via the GitHub web UI when convenient (gh CLI lacks `delete_repo` scope on this token).
- The old `chore/issue-templates` PR on curby ([#1](https://github.com/CasterlyGit/curby/pull/1)) — review and merge to land the issue templates on `main`.
- One-Project-per-repo vs one master Project: currently both. The hub aggregates everything; per-repo projects exist for focused boards. This is fine; revisit if the hub gets noisy.
- Auto-merge on green CI: not enabled. Always wait for human via PR review.
