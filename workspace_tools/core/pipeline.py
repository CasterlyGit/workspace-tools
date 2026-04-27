"""Pipeline = sequence of stages with deterministic Python control flow.

Critical property: stage progression is decided by THIS code, not by the model.
If a stage's agent says "Stop." or "Done.", we still move on to the next stage.
That's the whole point — fixes the brittleness of the markdown-prompt /iterate."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from .agent import Agent, AgentInvocation
from .git_ops import Repo, commit_paths
from .stage import Stage, StageContext, StageResult


@dataclass
class PipelineHooks:
    """Extension points. Each defaults to no-op. Future features (cost
    tracking, slack notifications, web dashboards, telemetry, retry/backoff,
    etc.) attach here without touching the pipeline core."""
    before_pipeline: Callable[[StageContext], None] | None = None
    before_stage:    Callable[[Stage, StageContext], None] | None = None
    after_stage:     Callable[[Stage, StageContext, StageResult], None] | None = None
    on_agent_line:   Callable[[Stage, str], None] | None = None
    after_pipeline:  Callable[[StageContext, list[StageResult]], None] | None = None


@dataclass
class PipelineRun:
    stage_results: list[StageResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None

    @property
    def all_ok(self) -> bool:
        return all(r.ok or r.skipped for r in self.stage_results)


class Pipeline:
    """Runs an ordered list of stages against a single context.

    Resumable by construction: a stage whose artifact already exists is
    skipped (logs as 'skipped: artifact present'). Re-running an interrupted
    pipeline picks up where it left off."""

    def __init__(self,
                 stages: list[Stage],
                 *,
                 agent: Agent | None = None,
                 hooks: PipelineHooks | None = None,
                 logger: Callable[[str], None] | None = None):
        self.stages = stages
        self.agent = agent or Agent()
        self.hooks = hooks or PipelineHooks()
        self.log = logger or (lambda s: print(s, flush=True))

    def run(self, ctx: StageContext, repo: Repo | None = None) -> PipelineRun:
        run = PipelineRun()
        ctx.flow_dir.mkdir(parents=True, exist_ok=True)

        if self.hooks.before_pipeline:
            self.hooks.before_pipeline(ctx)
        self.log(f"[pipeline] starting · {len(self.stages)} stage(s) · task={ctx.task_id}")

        for stage in self.stages:
            res = self._run_stage(stage, ctx, repo)
            run.stage_results.append(res)
            if not res.ok and not res.skipped:
                self.log(f"[pipeline] HALT after {stage.name}: {res.error}")
                break

        run.finished_at = datetime.now()
        if self.hooks.after_pipeline:
            self.hooks.after_pipeline(ctx, run.stage_results)
        elapsed = (run.finished_at - run.started_at).total_seconds()
        ok = sum(1 for r in run.stage_results if r.ok)
        sk = sum(1 for r in run.stage_results if r.skipped)
        self.log(f"[pipeline] done · ok={ok}  skipped={sk}  elapsed={elapsed:.1f}s")
        return run

    # ── internals ─────────────────────────────────────────────────────────────

    def _run_stage(self, stage: Stage, ctx: StageContext, repo: Repo | None) -> StageResult:
        artifact = ctx.flow_dir / stage.artifact_filename

        # Resume support: artifact already there → skip
        if artifact.exists():
            self.log(f"[stage:{stage.name}] skip (artifact present: {artifact.name})")
            return StageResult(skipped=True, artifact_path=artifact)

        # Custom skip predicate
        if stage.skip_when and stage.skip_when(ctx):
            self.log(f"[stage:{stage.name}] skip (skip_when fired)")
            return StageResult(skipped=True)

        # `reads` is advisory — log if a declared input is missing, but
        # don't halt. Lighter pipeline shapes (quickfix, bugfix) deliberately
        # skip earlier stages, so a missing REQUIREMENTS.md or DESIGN.md is
        # expected; the agent should adapt from the issue body + whatever
        # artifacts ARE present. Halting was forcing every shape to include
        # every dependency, which defeats the point of having lighter shapes.
        for read in stage.reads:
            if not (ctx.flow_dir / read).exists():
                self.log(f"[stage:{stage.name}] note: declared read '{read}' "
                         f"not present (pipeline shape skipped its producer); "
                         f"agent will work from the issue body + present artifacts")

        if self.hooks.before_stage:
            self.hooks.before_stage(stage, ctx)

        self.log(f"[stage:{stage.name}] running…")

        prompt = stage.render_prompt(ctx)
        on_line = (lambda s: self.hooks.on_agent_line(stage, s)) if self.hooks.on_agent_line else None
        inv = AgentInvocation(prompt=prompt, cwd=ctx.repo_path,
                              timeout_s=stage.timeout_s,
                              extra_args=stage.extra_args,
                              label=stage.name, on_line=on_line)
        result = self.agent.run(inv)

        if not result.ok:
            err = f"agent failed (rc={result.returncode}): {result.stderr[:200]}"
            self.log(f"[stage:{stage.name}] {err}")
            return StageResult(success=False, error=err, agent_stdout=result.stdout)

        if not artifact.exists():
            err = f"agent did not produce artifact {artifact.name}"
            self.log(f"[stage:{stage.name}] {err}")
            return StageResult(success=False, error=err, agent_stdout=result.stdout)

        # Commit just this stage's artifact (atomic per-stage commit)
        if repo is not None:
            try:
                commit_paths(repo, [artifact],
                             message=f"{stage.name}: {ctx.task_id} agent-generated artifact")
            except Exception as e:
                self.log(f"[stage:{stage.name}] commit failed: {e} (continuing)")

        sr = StageResult(success=True, artifact_path=artifact, agent_stdout=result.stdout)
        if self.hooks.after_stage:
            self.hooks.after_stage(stage, ctx, sr)
        self.log(f"[stage:{stage.name}] ok ({result.duration_s:.1f}s)")
        return sr
