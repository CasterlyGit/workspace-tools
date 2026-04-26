"""Stage registry. Each stage is a Stage instance with its prompt loaded from
stages/prompts/<name>.md. Add a new stage by:

    1. drop a prompt at workspace_tools/stages/prompts/<your_stage>.md
    2. construct a Stage() here, give it a unique name + artifact_filename
    3. include it in whatever pipeline shapes need it (workspace_tools/pipelines/)

Nothing else in the codebase knows the list of stages — Pipeline takes any list."""
from __future__ import annotations

from ..core.stage import Stage, load_prompt


EXPLORE = Stage(
    name="explore",
    artifact_filename="EXPLORE.md",
    reads=[],
    prompt_template=load_prompt("explore.md"),
    timeout_s=900,
)

RESEARCH = Stage(
    name="research",
    artifact_filename="RESEARCH.md",
    reads=["EXPLORE.md"],
    prompt_template=load_prompt("research.md"),
    timeout_s=900,
)

REQUIREMENTS = Stage(
    name="requirements",
    artifact_filename="REQUIREMENTS.md",
    reads=["RESEARCH.md"],
    prompt_template=load_prompt("requirements.md"),
    timeout_s=600,
)

DESIGN = Stage(
    name="design",
    artifact_filename="DESIGN.md",
    reads=["REQUIREMENTS.md"],
    prompt_template=load_prompt("design.md"),
    timeout_s=900,
)

TEST_PLAN = Stage(
    name="test-plan",
    artifact_filename="TEST_PLAN.md",
    reads=["REQUIREMENTS.md", "DESIGN.md"],
    prompt_template=load_prompt("test_plan.md"),
    timeout_s=600,
)

IMPLEMENT = Stage(
    name="implement",
    artifact_filename="IMPLEMENTATION.log",
    reads=["DESIGN.md", "TEST_PLAN.md"],
    prompt_template=load_prompt("implement.md"),
    timeout_s=2400,                       # 40 min — implementation can be long
)

INTEGRATION_TEST = Stage(
    name="integration-test",
    artifact_filename="INTEGRATION.md",
    reads=["REQUIREMENTS.md", "TEST_PLAN.md", "IMPLEMENTATION.log"],
    prompt_template=load_prompt("integration_test.md"),
    timeout_s=900,
)


__all__ = [
    "EXPLORE", "RESEARCH", "REQUIREMENTS", "DESIGN",
    "TEST_PLAN", "IMPLEMENT", "INTEGRATION_TEST",
]
