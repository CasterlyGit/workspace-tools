"""Pre-baked pipeline shapes. Each is just a `list[Stage]`.

# Fundamental principle: default to fast.

Most tickets are small. Multi-stage SDD pipelines spend most of their wall
clock and tokens re-exploring the repo, paraphrasing the ticket as
REQUIREMENTS.md, and paraphrasing the diff as DESIGN.md — work that buys
nothing for a one-file fix. So:

  - DEFAULT shape is `instant`: one Haiku call, reads the ticket, edits
    code, commits. Target: 60-180s wall clock.
  - `quickfix` adds an explore step (still Haiku) for tickets that need a
    bit of repo orientation.
  - `bugfix` keeps a real design doc (Sonnet) for genuine bugs where the
    theory of the fix matters.
  - `full` is the seven-stage SDD pipeline (Sonnet). Reserved for ambiguous
    features.

Escalate explicitly: a ticket can specify `pipeline: bugfix` or
`pipeline: full` in its body. The instant stage itself can also escalate
by writing `ESCALATE: <reason>` instead of code — the orchestrator surfaces
that and the user re-runs with a heavier shape.

Adding a new shape:
  - Compose Stage instances from `workspace_tools.stages`
  - Apply a model via `_with_model(stage, MODEL)`
  - Pipeline doesn't care; it runs whatever ordered list you give it.
"""
from __future__ import annotations

from dataclasses import replace

from .. import stages as S
from ..core.stage import Stage


# ── Models ────────────────────────────────────────────────────────────────
#
# Concrete model IDs in one place so swapping is one edit. Each shape picks
# from these. Per-stage overrides are possible but rarely worth it — if a
# stage needs more horsepower, that's evidence the ticket should run on a
# heavier shape.

MODEL_FAST    = "claude-haiku-4-5-20251001"   # instant, quickfix
MODEL_BALANCED = "claude-sonnet-4-6"          # bugfix, full
MODEL_HEAVY   = "claude-opus-4-7"             # opt-in only, never default


def _with_model(stage: Stage, model: str) -> Stage:
    """Return a copy of `stage` with `--model <model>` prepended to extra_args.

    Doesn't mutate the module-level Stage singletons in workspace_tools.stages,
    so the same Stage can appear in multiple shapes with different models."""
    return replace(stage, extra_args=["--model", model, *stage.extra_args])


# ── Shapes ────────────────────────────────────────────────────────────────

def instant() -> list[Stage]:
    """One agent call. No artifacts beyond INSTANT.log. ~60-180s.

    The default. Used unless the ticket explicitly requests heavier."""
    return [_with_model(S.INSTANT, MODEL_FAST)]


def feedback() -> list[Stage]:
    """Respond to PR feedback. Implement + test only. ~2-5 min.

    Used when there's user feedback on a PR. Skips explore/research/design/test-plan;
    agent reads the feedback and implements the delta."""
    return [_with_model(S.IMPLEMENT, MODEL_BALANCED),
            _with_model(S.INTEGRATION_TEST, MODEL_BALANCED)]


def quickfix() -> list[Stage]:
    """Explore + implement + integration-test. Fast model. ~3-5 min.

    For tickets where the agent needs to look around the repo before
    editing, but a design doc is overkill."""
    return [_with_model(S.EXPLORE, MODEL_FAST),
            _with_model(S.IMPLEMENT, MODEL_FAST),
            _with_model(S.INTEGRATION_TEST, MODEL_FAST)]


def bugfix() -> list[Stage]:
    """5-stage compact pipeline. Balanced model. ~5-10 min.

    Skips REQUIREMENTS (issue body = spec) and TEST_PLAN (regression test
    inside implement). Keeps DESIGN because real bugs benefit from a
    documented theory of the fix."""
    return [_with_model(S.EXPLORE, MODEL_BALANCED),
            _with_model(S.RESEARCH, MODEL_BALANCED),
            _with_model(S.DESIGN, MODEL_BALANCED),
            _with_model(S.IMPLEMENT, MODEL_BALANCED),
            _with_model(S.INTEGRATION_TEST, MODEL_BALANCED)]


def sdd_brownfield() -> list[Stage]:
    """Full 7-stage SDD pipeline. For substantial features. ~10-20 min."""
    return [_with_model(S.EXPLORE, MODEL_BALANCED),
            _with_model(S.RESEARCH, MODEL_BALANCED),
            _with_model(S.REQUIREMENTS, MODEL_BALANCED),
            _with_model(S.DESIGN, MODEL_BALANCED),
            _with_model(S.TEST_PLAN, MODEL_BALANCED),
            _with_model(S.IMPLEMENT, MODEL_BALANCED),
            _with_model(S.INTEGRATION_TEST, MODEL_BALANCED)]


def sdd_greenfield() -> list[Stage]:
    """Greenfield: skips explore (fresh repo). For /automate."""
    return [_with_model(S.RESEARCH, MODEL_BALANCED),
            _with_model(S.REQUIREMENTS, MODEL_BALANCED),
            _with_model(S.DESIGN, MODEL_BALANCED),
            _with_model(S.TEST_PLAN, MODEL_BALANCED),
            _with_model(S.IMPLEMENT, MODEL_BALANCED),
            _with_model(S.INTEGRATION_TEST, MODEL_BALANCED)]


SHAPES = {
    "instant":    instant,
    "fast":       instant,
    "feedback":   feedback,
    "quickfix":   quickfix,
    "polish":     quickfix,
    "chore":      quickfix,
    "bugfix":     bugfix,
    "bug":        bugfix,
    "full":       sdd_brownfield,
    "feature":    sdd_brownfield,
    "greenfield": sdd_greenfield,
}


def pick_shape(name: str | None, *, default: str = "instant") -> list[Stage]:
    """Resolve a shape by name. Falls back to `default` if name is None / unknown.

    Default is `instant` — see module docstring for why."""
    if name and name.lower() in SHAPES:
        return SHAPES[name.lower()]()
    return SHAPES[default]()


def shape_for_issue(labels: list[str], body: str) -> str:
    """Heuristic — pick a sensible default shape from the issue's labels + body.

    Order of precedence:
      1. Explicit magic line in body: `pipeline: bugfix` (or instant/full/etc.)
      2. Labels: feature → full, bug → bugfix, polish/chore → quickfix
      3. Otherwise: `instant` (the default — see module docstring)

    The orchestrator never picks for you silently — it logs the chosen shape
    so you see why it ran what it did. The instant stage can also escalate
    itself by writing `ESCALATE: …` to its log."""
    import re
    m = re.search(r"^pipeline:\s*(\w+)\s*$", body or "", re.MULTILINE | re.IGNORECASE)
    if m and m.group(1).lower() in SHAPES:
        return m.group(1).lower()

    label_set = {l.lower() for l in labels}
    if "feature" in label_set:
        return "full"
    if "bug" in label_set:
        return "bugfix"
    if "polish" in label_set or "chore" in label_set or "docs" in label_set:
        return "quickfix"

    # No labels, no magic line. Trust the default. The instant stage will
    # escalate if it can't make a confident change.
    return "instant"


__all__ = [
    "instant", "quickfix", "bugfix", "sdd_brownfield", "sdd_greenfield",
    "SHAPES", "pick_shape", "shape_for_issue",
    "MODEL_FAST", "MODEL_BALANCED", "MODEL_HEAVY",
]
