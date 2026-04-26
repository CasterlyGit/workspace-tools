"""Pre-baked pipeline shapes. Each is just a `list[Stage]`.

Adding a new shape:
  - Compose Stage instances from `workspace_tools.stages`
  - Or build a custom one inline
  - Pipeline doesn't care; it runs whatever ordered list you give it.
"""
from __future__ import annotations

from .. import stages as S
from ..core.stage import Stage


def sdd_brownfield() -> list[Stage]:
    """Full 7-stage SDD pipeline for an existing repo + filed issue.

    Drives /iterate."""
    return [S.EXPLORE, S.RESEARCH, S.REQUIREMENTS, S.DESIGN,
            S.TEST_PLAN, S.IMPLEMENT, S.INTEGRATION_TEST]


def sdd_greenfield() -> list[Stage]:
    """Same as brownfield but skips explore (fresh repo, nothing to map).

    Drives /automate."""
    return [S.RESEARCH, S.REQUIREMENTS, S.DESIGN,
            S.TEST_PLAN, S.IMPLEMENT, S.INTEGRATION_TEST]


__all__ = ["sdd_brownfield", "sdd_greenfield"]
