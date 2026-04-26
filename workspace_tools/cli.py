"""Workspace-tools CLI.

Two top-level commands today:

    workspace-tools iterate <issue-url|owner/repo#N|next>
    workspace-tools automate "<idea>"

Both run their pipeline deterministically: stages execute in Python, not via
a model loop. If a stage fails, the orchestrator halts and reports — there's
no silent "Stop." that ends a multi-stage run prematurely.

Adding a new top-level command is one new sub-parser + one function below.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import (
    Agent, Pipeline, PipelineHooks, Repo, StageContext,
    ensure_branch, push, pr_create, pr_open_for_branch,
    fetch_issue, parse_issue_ref, slugify,
)
from .pipelines import sdd_brownfield


def cmd_iterate(args: argparse.Namespace) -> int:
    issue_ref = args.issue
    repo_full, num = parse_issue_ref(issue_ref)
    issue = fetch_issue(repo_full, num)

    # Locate or assume the local repo at ~/Documents/Dev/<name>
    dev = Path.home() / "Documents" / "Dev"
    repo_path = dev / issue.repo_name
    if not (repo_path / ".git").is_dir():
        print(f"[iterate] no local clone at {repo_path}; cloning…", flush=True)
        from subprocess import run as srun
        srun(["gh", "repo", "clone", repo_full, str(repo_path)], check=True)

    repo = Repo.at(repo_path)
    branch = f"auto/{issue.number}-{slugify(issue.title)}"
    ensure_branch(repo, branch)

    flow_dir = repo_path / ".flow" / f"issue-{issue.number}"
    ctx = StageContext(
        repo_path=repo_path,
        flow_dir=flow_dir,
        task_id=f"issue-{issue.number}",
        issue_text=issue.aggregated_text(),
        issue_url=issue.url,
        extra={"branch": branch, "repo": repo},
    )

    # ── log lines stream live to stdout, prefixed by stage name ──────────
    def on_line(stage, line):
        if line.strip():
            print(f"[{stage.name}] {line[:200]}", flush=True)

    hooks = PipelineHooks(on_agent_line=on_line)
    pipeline = Pipeline(stages=sdd_brownfield(), agent=Agent(), hooks=hooks)
    run = pipeline.run(ctx, repo=repo)

    if not run.all_ok:
        print(f"\n[iterate] pipeline halted; partial branch left at {branch}", flush=True)
        return 2

    # Push the branch + open PR (or update existing)
    push(repo, branch)
    existing = pr_open_for_branch(repo, branch)
    if existing:
        print(f"[iterate] PR already open: {existing['url']}", flush=True)
        pr_url = existing["url"]
    else:
        title = issue.title
        body = (
            f"Closes #{issue.number}.\n\n"
            f"All 7 SDD stages ran via workspace-tools orchestrator. "
            f"Spec artifacts under `.flow/issue-{issue.number}/`.\n"
        )
        pr = pr_create(repo, title=title, body=body, base="main", head=branch,
                       labels=issue.labels or None)
        pr_url = pr["url"]
        print(f"\n[iterate] PR opened: {pr_url}", flush=True)

    return 0


def cmd_automate(args: argparse.Namespace) -> int:
    print("[automate] not yet implemented in the new orchestrator — coming next.", flush=True)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workspace-tools",
                                     description="Deterministic SDD pipeline runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_it = sub.add_parser("iterate", help="run the SDD pipeline against a GitHub issue")
    p_it.add_argument("issue", help="full issue URL, owner/repo#N, or 'next' for top of project board")

    p_au = sub.add_parser("automate", help="greenfield: turn an idea into a new project")
    p_au.add_argument("idea", help="one-line description of what to build")

    args = parser.parse_args(argv)
    if args.cmd == "iterate":
        return cmd_iterate(args)
    if args.cmd == "automate":
        return cmd_automate(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
