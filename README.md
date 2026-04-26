# workspace-tools

A small Python package that runs your personal SDD (spec-driven development)
pipelines deterministically. Replaces the markdown-prompt `/iterate` skill —
which was brittle (a stage prompt saying _"Stop."_ would end a multi-stage run
early) — with a Python orchestrator that loops through stages explicitly.

## What's in here

```
workspace_tools/
├── core/
│   ├── agent.py          # wraps `claude --print`. Swap providers here.
│   ├── stage.py          # Stage = name + artifact + reads + prompt template
│   ├── pipeline.py       # Pipeline = list[Stage] + run() with resume + hooks
│   ├── git_ops.py        # branch, commit, push, PR helpers (gh CLI)
│   └── issue.py          # gh issue fetch + parsing
├── stages/
│   ├── prompts/          # one .md file per stage. Edit a prompt → next run uses it.
│   └── __init__.py       # registry: EXPLORE, RESEARCH, REQUIREMENTS, ...
├── pipelines/
│   └── __init__.py       # pre-baked shapes: sdd_brownfield(), sdd_greenfield()
└── cli.py                # `iterate` and `automate` subcommands
```

## Running it

```bash
cd ~/Documents/Dev/workspace-tools
python -m workspace_tools.cli iterate https://github.com/CasterlyGit/curby/issues/13
```

It will:

1. Fetch the issue (title, body, comments).
2. Ensure the local clone exists at `~/Documents/Dev/<repo>/`.
3. Switch to (or create) `auto/<N>-<slug>` branch.
4. Run each stage in order: explore → research → requirements → design → test-plan → implement → integration-test.
5. After each stage, verify the artifact and commit it.
6. After all stages, push the branch and open a PR.

**Resume**: re-running on the same issue picks up where it stopped. Each
stage skips itself if its artifact already exists on disk (i.e. a previous
run produced it). Delete the artifact under `<repo>/.flow/issue-N/` to force
that stage to re-run.

## Extension points (the future-proofing)

### Add a new stage

1. Drop `workspace_tools/stages/prompts/security_review.md` (your prompt).
2. In `stages/__init__.py`:
   ```python
   SECURITY_REVIEW = Stage(
       name="security-review",
       artifact_filename="SECURITY_REVIEW.md",
       reads=["DESIGN.md"],
       prompt_template=load_prompt("security_review.md"),
       timeout_s=600,
   )
   ```
3. Compose into a pipeline:
   ```python
   def sdd_brownfield_with_security():
       return [S.EXPLORE, S.RESEARCH, S.REQUIREMENTS,
               S.DESIGN, S.SECURITY_REVIEW,
               S.TEST_PLAN, S.IMPLEMENT, S.INTEGRATION_TEST]
   ```
4. Register a new CLI subcommand or env-flag to pick the new shape.

No core changes. Pipeline doesn't care how many stages.

### Add a new provider (different LLM, local model, etc.)

Subclass `Agent` (or replace it). The contract is one method:

```python
class MyAgent(Agent):
    def run(self, inv: AgentInvocation) -> AgentResult:
        ...
```

Pass `Pipeline(stages=..., agent=MyAgent())` and you're done.

### Add hooks (cost tracking, slack notifications, dashboards, retries)

`PipelineHooks` has `before_stage`, `after_stage`, `on_agent_line`,
`before_pipeline`, `after_pipeline`. Each is `None` by default; pass a callable
to wire it up:

```python
def to_slack(stage, ctx, result):
    requests.post(SLACK, json={"text": f"{stage.name}: {result.ok}"})

hooks = PipelineHooks(after_stage=to_slack)
Pipeline(stages=..., hooks=hooks).run(ctx, repo)
```

### Different pipeline shapes for different ticket types

Add functions to `pipelines/__init__.py`:

```python
def hotfix() -> list[Stage]:
    return [S.RESEARCH, S.IMPLEMENT, S.INTEGRATION_TEST]

def docs_only() -> list[Stage]:
    return [S.EXPLORE, S.IMPLEMENT, S.INTEGRATION_TEST]
```

Pick which one to run based on the issue's labels / your magic line / a CLI flag.

### Parallel stages, retry, conditional skips

All possible without touching `Pipeline` — most fit naturally as `Stage`
subclasses or as hooks. If parallel stages become a thing, `Pipeline.run()`
gains a small DAG mode (~20 lines). The current sequential flow stays the
default.

## Why this exists

The original `/iterate` was a markdown skill that asked the model to invoke
seven sub-skills in order. The model occasionally read a sub-skill's
"Stop after writing the artifact" instruction and ended the run after stage 1.
Recovery required killing the hung process and re-running.

This package moves the loop into Python so:

- Each stage is invoked deterministically by the orchestrator.
- The orchestrator decides when to move on, not the model.
- A failing stage halts the pipeline cleanly with a clear log line.
- Resume just works (artifacts on disk = stage already done).
- Adding stages, providers, or hooks doesn't require model-prompt gymnastics.

## Install the slash command

```bash
./scripts/install-skills.sh
```

Backs up the existing `~/.claude/commands/iterate.md` and replaces it with a
thin wrapper that shells out to `python -m workspace_tools.cli iterate ...`.

## License

MIT.
