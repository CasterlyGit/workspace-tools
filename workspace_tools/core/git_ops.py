"""Thin wrappers around git + gh that the orchestrator needs.

Kept tiny on purpose: these are the only git/gh calls in the codebase, so when
we change branch naming, commit conventions, PR template, or even swap from
GitHub to a different forge, it's all one file."""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


def run(cmd: list[str], cwd: Path | str | None = None, check: bool = True) -> str:
    """Run a shell command, return stdout. Raises on non-zero unless check=False."""
    res = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                         capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{res.stderr}")
    return res.stdout.strip()


def slugify(text: str, maxlen: int = 30) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower())
    return s.strip("-")[:maxlen].rstrip("-") or "task"


@dataclass
class Repo:
    path: Path
    owner: str
    name: str

    @property
    def full(self) -> str:
        return f"{self.owner}/{self.name}"

    @classmethod
    def at(cls, path: Path) -> "Repo":
        info = json.loads(run(["gh", "repo", "view", "--json", "owner,name"], cwd=path))
        return cls(path=path, owner=info["owner"]["login"], name=info["name"])


def current_branch(repo: Repo) -> str:
    return run(["git", "branch", "--show-current"], cwd=repo.path)


def ensure_branch(repo: Repo, branch: str, base: str = "main") -> None:
    """Switch to `branch`, creating it from latest `base` if absent.

    If we're already on `branch`, do nothing. If `branch` exists locally, just
    switch to it without rebasing — preserves any in-flight work."""
    if current_branch(repo) == branch:
        return
    # Try to switch to existing branch
    res = subprocess.run(["git", "switch", branch], cwd=repo.path, capture_output=True, text=True)
    if res.returncode == 0:
        return
    # Create from base
    run(["git", "fetch", "origin", base], cwd=repo.path, check=False)
    run(["git", "switch", base], cwd=repo.path)
    run(["git", "pull", "--ff-only"], cwd=repo.path, check=False)
    run(["git", "switch", "-c", branch], cwd=repo.path)


def commit_paths(repo: Repo, paths: list[str | Path], message: str) -> bool:
    """Stage + commit specific paths. Returns True if a commit was actually made
    (i.e. there were changes), False if nothing to commit."""
    args = ["git", "add", *map(str, paths)]
    run(args, cwd=repo.path)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo.path)
    if diff.returncode == 0:
        return False  # nothing staged
    run(["git", "commit", "-m", message], cwd=repo.path)
    return True


def push(repo: Repo, branch: str, set_upstream: bool = True) -> None:
    args = ["git", "push"]
    if set_upstream:
        args += ["-u", "origin", branch]
    run(args, cwd=repo.path, check=False)


def pr_open_for_branch(repo: Repo, branch: str) -> dict | None:
    """Return the dict for an open PR on this branch, or None."""
    out = run(["gh", "pr", "list", "--repo", repo.full, "--state", "open",
               "--head", branch, "--json", "number,url,title,state"], cwd=repo.path)
    items = json.loads(out or "[]")
    return items[0] if items else None


def pr_create(repo: Repo, *, title: str, body: str, base: str = "main",
              head: str | None = None, labels: list[str] | None = None) -> dict:
    args = ["gh", "pr", "create", "--repo", repo.full,
            "--title", title, "--body", body, "--base", base]
    if head:
        args += ["--head", head]
    if labels:
        args += ["--label", ",".join(labels)]
    url = run(args, cwd=repo.path).strip().splitlines()[-1]
    num = int(url.rsplit("/", 1)[-1]) if url.startswith("https://") else 0
    return {"number": num, "url": url}
