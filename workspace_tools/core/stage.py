"""Stage = one step of a pipeline.

A Stage is just a small object with:
  - a name
  - an artifact filename it writes
  - prerequisite artifacts it reads
  - a prompt template that asks the agent to produce that artifact
  - optional skip predicate

Adding a new stage is one new Python file under stages/ + one prompt file. The
pipeline machinery is unchanged."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class StageContext:
    """Everything a stage needs to do its work, passed by Pipeline."""
    repo_path: Path
    flow_dir: Path                  # <repo>/.flow/<task-id>/
    task_id: str                    # e.g. "issue-13" or "init"
    issue_text: str                 # title + body + comments (or the idea, for greenfield)
    issue_url: str                  # may be empty for greenfield
    user_feedback: str = ""         # last comment on the issue/PR (amend feedback)
    extra: dict = field(default_factory=dict)   # free-form for callers / future hooks


@dataclass
class StageResult:
    skipped: bool = False
    success: bool = True
    artifact_path: Path | None = None
    error: str | None = None
    agent_stdout: str = ""

    @property
    def ok(self) -> bool:
        return self.success and not self.error


@dataclass
class Stage:
    name: str                          # short slug, used in commit messages: "explore", "design", ...
    artifact_filename: str             # what gets written under flow_dir
    reads: list[str] = field(default_factory=list)   # other artifact filenames this stage depends on
    prompt_template: str = ""          # rendered with str.format(**context); the agent prompt
    skip_when: Callable[[StageContext], bool] | None = None
    extra_args: list[str] = field(default_factory=list)
    timeout_s: int = 1200              # 20 min default per stage

    def render_prompt(self, ctx: StageContext) -> str:
        return self.prompt_template.format(
            task_id=ctx.task_id,
            flow_dir=ctx.flow_dir,
            repo_path=ctx.repo_path,
            issue_text=ctx.issue_text,
            issue_url=ctx.issue_url,
            user_feedback=ctx.user_feedback,
            artifact_path=ctx.flow_dir / self.artifact_filename,
            reads=", ".join(str(ctx.flow_dir / r) for r in self.reads),
        )


def load_prompt(filename: str) -> str:
    """Convenience: read a prompt template shipped alongside the stages package."""
    path = Path(__file__).resolve().parent.parent / "stages" / "prompts" / filename
    return path.read_text(encoding="utf-8")
